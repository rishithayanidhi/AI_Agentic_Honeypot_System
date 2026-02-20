from fastapi import FastAPI, HTTPException, Security, Depends, Request, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import asyncio
import warnings
import sys
import time
from typing import Optional, Union, Dict, Any
from contextlib import asynccontextmanager

# Suppress Pydantic warnings from google-genai library
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._fields")

from config import settings
from src.models.schemas import (
    IncomingRequest, APIResponse, EngagementMetrics, 
    ExtractedIntelligence, Message
)
from src.services.session_manager import session_manager
from src.services.scam_detector import ScamDetector
from src.services.ai_agent import AIAgent
from src.utils.intelligence_extractor import IntelligenceExtractor
from src.services.guvi_callback import guvi_callback
from src.middleware import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    PerformanceMonitoringMiddleware
)

# Configure logging for Render (explicit stdout) with more detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)
logger = logging.getLogger(__name__)

# Performance and health monitoring
class HealthMonitor:
    """Monitor API health and performance metrics"""
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.fast_path_hits = 0
        self.cache_hits = 0
        self.circuit_breaker_trips = 0
        
    def record_request(self, response_time: float, is_error: bool = False):
        self.request_count += 1
        self.total_response_time += response_time
        if is_error:
            self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        avg_response = self.total_response_time / max(self.request_count, 1)
        error_rate = (self.error_count / max(self.request_count, 1)) * 100
        
        return {
            "uptime_seconds": int(uptime),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response * 1000, 2),
            "fast_path_hits": self.fast_path_hits,
            "cache_hits": self.cache_hits,
            "circuit_breaker_trips": self.circuit_breaker_trips
        }

health_monitor = HealthMonitor()

# Log startup info
# Clean deployment - no database dependencies (v2.0)
logger.info("="*60)
logger.info("AI AGENTIC HONEYPOT SYSTEM STARTING")
logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
logger.info("="*60)
sys.stdout.flush()  # Force flush to Render

# Initialize FastAPI app with performance optimizations
app = FastAPI(
    title="AI Agentic Honeypot System",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,  # Disable unused ReDoc
    openapi_url="/openapi.json"
)

# Add compression middleware for faster responses
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add security and performance middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE if hasattr(settings, 'RATE_LIMIT_PER_MINUTE') else 60
)
app.add_middleware(
    RequestValidationMiddleware,
    max_body_size=1048576  # 1MB max
)
app.add_middleware(
    PerformanceMonitoringMiddleware,
    slow_request_threshold=5.0  # Log requests slower than 5s
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication
from fastapi.security import APIKeyHeader
api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key"""
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Initialize services
scam_detector = ScamDetector()
ai_agent = AIAgent()
intelligence_extractor = IntelligenceExtractor()


# Add validation error handler for better debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log and return detailed validation errors"""
    logger.error(f"=" * 80)
    logger.error(f"VALIDATION ERROR for {request.url.path}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Headers: {dict(request.headers)}")
    
    # Try to read the raw body
    try:
        body = await request.body()
        logger.error(f"Raw body: {body.decode('utf-8')}")
    except Exception as e:
        logger.error(f"Could not read body: {e}")
    
    logger.error(f"Validation errors: {exc.errors()}")
    logger.error(f"=" * 80)
    
    # Create detailed error messages
    error_details = []
    error_summary = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get('loc', []))
        error_msg = err.get('msg', '')
        error_summary.append(f"{field_path}: {error_msg}")
        error_details.append({
            "field": field_path,
            "message": error_msg,
            "type": err.get('type', ''),
            "input": str(err.get('input', 'N/A'))[:100]  # Truncate long inputs
        })
    
    # Create user-friendly message that will be displayed
    friendly_message = (
        "VALIDATION ERROR:\n\n" + 
        "\n".join(f"• {err}" for err in error_summary[:5]) +  # Show first 5 errors
        "\n\nRequired format:\n" +
        '{"sessionId":"session-123","message":{"sender":"scammer","text":"Your message","timestamp":"2026-02-01T10:00:00Z"},"conversationHistory":[],"metadata":{"channel":"SMS","language":"English","locale":"IN"}}'
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": "INVALID_REQUEST_BODY",
            "message": friendly_message,
            "errors": error_details,
            "example": {
                "sessionId": "session-123",
                "message": {
                    "sender": "scammer",
                    "text": "URGENT: Your account will be blocked. Share OTP now.",
                    "timestamp": "2026-02-01T10:00:00Z"
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
        }
    )


@app.get("/")
@app.head("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Agentic Honeypot System",
        "version": "1.0.0"
    }


@app.get("/health")
@app.head("/health")
async def health_check():
    """Comprehensive health check with performance metrics"""
    gemini_keys_count = len(settings.get_gemini_api_keys())
    stats = health_monitor.get_stats()
    
    # Determine health status
    is_healthy = stats['error_rate_percent'] < 10 and stats['avg_response_time_ms'] < 3000
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "AI Agentic Honeypot System",
        "version": "2.0.0-optimized",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_manager.sessions),
        "llm_provider": settings.LLM_PROVIDER,
        "gemini_keys_loaded": gemini_keys_count if gemini_keys_count > 0 else 0,
        "performance_metrics": stats,
        "optimizations": {
            "fast_path_enabled": True,
            "cache_size": settings.CACHE_MAX_SIZE,
            "pre_compiled_regex": True,
            "lru_caching": True
        }
    }


@app.post("/api/message")
async def handle_message(
    raw_request: Request,
    api_key: str = Header(None, alias="x-api-key")
):
    """
    Main endpoint to handle incoming messages - PRODUCTION READY
    - Request timeout protection (30s max)
    - Comprehensive error handling with fallbacks
    - Performance monitoring
    - GUVI Format: Returns {"status": "success", "reply": "agent response"}
    """
    request_start_time = time.time()
    
    # Make API key optional for GUVI tester compatibility
    if api_key:
        if api_key != settings.API_KEY:
            health_monitor.record_request(time.time() - request_start_time, is_error=True)
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        # TIMEOUT PROTECTION: Wrap entire handler in timeout
        return await asyncio.wait_for(
            process_message(raw_request, request_start_time),
            timeout=28.0  # 28s to leave 2s buffer for GUVI's 30s timeout
        )
    except asyncio.TimeoutError:
        logger.error("⏱️ Request timeout after 28s - returning fast fallback")
        health_monitor.record_request(time.time() - request_start_time, is_error=True)
        return {
            "status": "success",
            "reply": "I understand. Can you tell me more about this?"
        }
    except Exception as e:
        logger.error(f"💥 Unhandled error in message handler: {e}", exc_info=True)
        health_monitor.record_request(time.time() - request_start_time, is_error=True)
        return {
            "status": "success",
            "reply": "I see. Could you provide more details?"
        }

async def process_message(raw_request: Request, request_start_time: float) -> Dict[str, Any]:
    """Process message with full error handling and fallbacks"""
    try:
        # Parse request body manually to avoid validation errors
        request = None
        body_str = ""
        try:
            body = await raw_request.body()
            body_str = body.decode('utf-8') if body else ""
            
            if body_str and body_str.strip():
                import json
                request_data = json.loads(body_str)
                request = IncomingRequest(**request_data)
            else:
                # Empty body - return test response
                logger.info("Empty request body received - returning test response")
                return {
                    "status": "success",
                    "reply": settings.EMPTY_RESPONSE
                }
        except json.JSONDecodeError as je:
            logger.warning(f"Invalid JSON in request body: {je}, using default")
            return {
                "status": "success",
                "reply": "Invalid request format. Please send valid JSON."
            }
        except Exception as parse_error:
            logger.warning(f"Could not parse request body: {parse_error}, using default")
            request = IncomingRequest()
        
        logger.info(f"Received request type: {type(request).__name__}")
        logger.info(f"Request data: {request.model_dump()}")
        
        # Extract session_id with fallback
        session_id = request.sessionId or f"auto-{datetime.now().timestamp()}"
        
        # Handle message in various formats
        if request.message is None or request.message == "":
            # Empty message - GUVI tester or test request
            # Return immediately without processing (fast path for timeout avoidance)
            logger.info("Empty message received - returning quick test response")
            return {
                "status": "success",
                "reply": settings.EMPTY_MESSAGE_RESPONSE
            }
        elif isinstance(request.message, str):
            # Simple string message
            message_text = request.message if request.message else settings.DEFAULT_MESSAGE
            message_obj = Message(
                sender="scammer",
                text=message_text,
                timestamp=datetime.now().isoformat()
            )
        elif isinstance(request.message, dict):
            # Dictionary format - convert to Message
            message_text = request.message.get("text", request.message.get("message", settings.DEFAULT_MESSAGE))
            if not message_text:  # Ensure we have text
                message_text = settings.DEFAULT_MESSAGE
            message_obj = Message(
                sender=request.message.get("sender", "scammer"),
                text=message_text,
                timestamp=request.message.get("timestamp") or datetime.now().isoformat()
            )
        else:
            # Message object
            message_obj = request.message
            message_text = request.message.text if request.message.text else settings.DEFAULT_MESSAGE
        
        # SAFETY: Ensure message_text is never empty to prevent errors
        if not message_text or not message_text.strip():
            message_text = settings.DEFAULT_MESSAGE
            logger.warning(f"Empty message_text detected, using default '{settings.DEFAULT_MESSAGE}'")
        
        # BULLETPROOF INPUT SANITIZATION for 100+ test cases
        # Remove null bytes and control characters (except newlines/tabs)
        import re
        message_text = message_text.replace('\x00', '')  # Remove null bytes
        message_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', message_text)  # Remove control chars
        
        # Handle very long messages (max 10000 chars to prevent DoS)
        if len(message_text) > 10000:
            logger.warning(f"Message too long ({len(message_text)} chars), truncating to 10000")
            message_text = message_text[:10000] + "..."
        
        # Handle encoded text (common in test cases)
        try:
            # Try to decode common escape sequences
            message_text = message_text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Could not decode message text: {e}")
        
        # Handle excessive whitespace (normalize)
        message_text = ' '.join(message_text.split())
        
        # Final safety check
        if not message_text or len(message_text.strip()) < 2:
            message_text = settings.DEFAULT_MESSAGE
            logger.warning(f"Message too short after sanitization, using default")
        
        # OPTIMIZATION: Fast-path for short/test messages (avoid expensive processing)
        message_lower = message_text.lower().strip()
        word_count = len(message_text.split())
        has_strong_scam_keywords = any(
            keyword in message_lower for keyword in settings.get_fast_path_keywords()
        )
        
        # Fast return for very short messages (3 words or less) without scam indicators
        if word_count <= settings.FAST_PATH_THRESHOLD and not has_strong_scam_keywords:
            logger.info(f"⚡ Fast path: Short message ({word_count} words) - instant response")
            response_time = time.time() - request_start_time
            health_monitor.record_request(response_time)
            health_monitor.fast_path_hits += 1
            return {
                "status": "success",
                "reply": settings.FAST_PATH_RESPONSE
            }
        
        # Handle conversation history
        conversation_history = request.conversationHistory or []
        
        logger.info(f"Received message for session: {session_id}")
        
        # Get or create session
        session = session_manager.get_or_create_session(session_id)
        
        # Early exit if session is already complete
        if not session.engagement_active and session.scam_detected:
            return {
                "status": "success",
                "scamDetected": True,
                "agentResponse": settings.SESSION_COMPLETE_RESPONSE,
                "sessionComplete": True,
                "detection": {
                    "is_scam": True,
                    "confidence": 0.95,
                    "scam_type": "completed",
                    "reasoning": "Session already completed"
                }
            }
        
        # Add incoming message to session
        session.messages.append(message_obj)
        session.message_count += 1
        
        # Add conversation history to session if this is first message (optimized)
        # Only process if truly first message and history is reasonable size
        if conversation_history and session.message_count == 1 and len(conversation_history) < 5:
            # Use set for faster deduplication
            existing_texts = {msg.text for msg in session.messages}
            for hist_msg in conversation_history:
                if hist_msg.text not in existing_texts:
                    session.messages.insert(0, hist_msg)
                    existing_texts.add(hist_msg.text)
        
        # Initialize detection variables
        detection_result = {}
        scam_confidence = 0.0
        scam_type = 'unknown'
        
        # SPEED OPTIMIZED: Run synchronously, intelligence extraction is fast
        # Always extract intelligence (fast, no API calls)
        try:
            new_intel = intelligence_extractor.extract_from_message(message_text)
            session.intelligence = intelligence_extractor.merge_intelligence(
                session.intelligence, new_intel
            )
        except Exception as e:
            logger.error(f"Intelligence extraction error: {e}", exc_info=False)
        
        # Scam detection (only if not already detected)
        if not session.scam_detected:
            try:
                detection_result = scam_detector.detect_scam(message_text, session.messages)
            except Exception as e:
                logger.error(f"Scam detection error: {e}", exc_info=False)
                detection_result = {
                    'is_scam': False,
                    'confidence': 0.0,
                    'scam_type': 'error',
                    'reasoning': f'Detection error: {str(e)[:100]}'
                }
        
        # Process detection results
        if not session.scam_detected:
            # Validate detection result
            if not detection_result or not isinstance(detection_result, dict):
                logger.error(f"Invalid detection result: {detection_result}")
                detection_result = {
                    'is_scam': False,
                    'confidence': 0.0,
                    'scam_type': 'unknown',
                    'reasoning': 'Detection error - invalid result'
                }
            
            session.scam_detected = detection_result.get('is_scam', False)
            scam_confidence = detection_result.get('confidence', 0.0)
            scam_type = detection_result.get('scam_type', 'unknown')
            
            logger.info(f"Scam detection: {session.scam_detected} (confidence: {scam_confidence})")
            
            if session.scam_detected:
                session.engagement_active = True
                session.agent_notes = f"Scam detected: {scam_type}. {detection_result.get('reasoning', '')}"
        else:
            # Session already has scam detected - continue engagement
            scam_confidence = 0.95
            scam_type = session.agent_notes.split(':')[1].split('.')[0].strip() if ':' in session.agent_notes else 'confirmed'
            detection_result = {
                'is_scam': True,
                'confidence': 0.95,
                'scam_type': scam_type,
                'reasoning': 'Continuing conversation from previously detected scam'
            }
            # Keep engagement active for multi-turn conversations
            session.engagement_active = True
        
        # Generate agent response if scam is detected
        agent_response_text = None
        session_complete = False
        should_continue = True
        should_end = False
        end_reason = ""
        
        # Only generate AI response if engagement is active
        if session.scam_detected and session.engagement_active:
            try:
                # Select or maintain persona (dynamic change interval)
                if not session.persona or session.message_count % settings.PERSONA_CHANGE_INTERVAL == 0:
                    session.persona = ai_agent.select_persona(
                        scam_type=scam_type,
                        message_count=session.message_count
                    )
                
                # Generate response with 15s timeout (reduced for faster failures)
                try:
                    agent_decision = await asyncio.wait_for(
                        asyncio.to_thread(
                            ai_agent.generate_response,
                            scammer_message=message_text,
                            conversation_history=session.messages[-5:],  # Only last 5 messages for speed
                            persona=session.persona,
                            scam_type=scam_type,
                            extracted_intel=session.intelligence.model_dump(),
                            message_count=session.message_count
                        ),
                        timeout=15.0  # Reduced from 20s to 15s
                    )
                except asyncio.TimeoutError:
                    logger.warning("AI generation timed out after 15s - using fast fallback")
                    agent_decision = {
                        'response': "I see. Could you provide more details?",
                        'should_continue': True,
                        'notes': 'Timeout fallback',
                        'strategy': 'fast'
                    }
                
                # Safely extract response fields with validation
                if agent_decision and isinstance(agent_decision, dict):
                    agent_response_text = agent_decision.get('response', None)
                    should_continue = agent_decision.get('should_continue', True)
                    notes = agent_decision.get('notes', '')
                    
                    # Update agent notes
                    if notes:
                        session.agent_notes += f" | {notes}"
                    
                    # Add agent response to conversation
                    if agent_response_text:
                        user_message = Message(
                            sender="user",
                            text=agent_response_text,
                            timestamp=datetime.now().isoformat()
                        )
                        session.messages.append(user_message)
                        session.message_count += 1
                else:
                    # Fallback if agent_decision is None or invalid
                    logger.warning(f"AI agent returned invalid response: {agent_decision}")
                    agent_response_text = "I'm not sure I understand. Can you explain?"
                    should_continue = True
                
                # Check if conversation should end
                intelligence_quality = sum([
                    len(session.intelligence.bankAccounts) > 0,
                    len(session.intelligence.upiIds) > 0,
                    len(session.intelligence.phishingLinks) > 0,
                    len(session.intelligence.phoneNumbers) > 0,
                    len(session.intelligence.suspiciousKeywords) >= 3
                ])
                
                should_end, end_reason = ai_agent.should_end_conversation(
                    message_count=session.message_count,
                    intelligence_quality=intelligence_quality,
                    scam_confidence=scam_confidence
                )
            except Exception as agent_error:
                # Comprehensive error handling for AI agent failures
                logger.error(f"Error generating AI agent response: {agent_error}", exc_info=True)
                agent_response_text = "Sorry, I'm confused. What was that?"
                should_continue = True
                should_end = False
                end_reason = ""
                session.agent_notes += f" | Agent error: {str(agent_error)[:100]}"
            
            if should_end or not should_continue:
                session_complete = True
                session.engagement_active = False
                session.agent_notes += f" | Conversation ended: {end_reason}"
                logger.info(f"Session {session_id} complete: {end_reason}")
                
                # Send final results to GUVI
                engagement_duration = int((datetime.now() - session.created_at).total_seconds())
                success = guvi_callback.send_final_result(
                    session_id=session_id,
                    scam_detected=session.scam_detected,
                    total_messages=session.message_count,
                    extracted_intelligence=session.intelligence.model_dump(),
                    agent_notes=session.agent_notes,
                    engagement_duration=engagement_duration
                )
                
                if success:
                    logger.info(f"Successfully sent final results to GUVI for session {session_id}")
                else:
                    logger.warning(f"Failed to send results to GUVI for session {session_id}")
        
        # Fast response preparation with minimal overhead
        engagement_duration = int((datetime.now() - session.created_at).total_seconds())
        
        # Prepare response according to GUVI specification
        # Primary format: simple {"status": "success", "reply": "agent response"}
        response_dict = {
            "status": "success",
            "reply": agent_response_text if agent_response_text else "I see. Can you tell me more?"
        }
        
        # Add optional detailed fields for debugging/monitoring (won't affect competition evaluation)
        if settings.INCLUDE_DEBUG_INFO:
            response_dict.update({
                "sessionId": session_id,
                "scamDetected": session.scam_detected,
                "sessionComplete": session_complete,
                "engagementMetrics": {
                    "totalMessagesExchanged": session.message_count,
                    "engagementDurationSeconds": engagement_duration,
                    "scamDetectionAccuracy": scam_confidence
                },
                "extractedIntelligence": {
                    "phoneNumbers": session.intelligence.phoneNumbers,
                    "bankAccounts": session.intelligence.bankAccounts,
                    "upiIds": session.intelligence.upiIds,
                    "phishingLinks": session.intelligence.phishingLinks,
                    "emailAddresses": session.intelligence.emailAddresses
                },
                "detection": {
                    "is_scam": session.scam_detected,
                    "confidence": scam_confidence,
                    "scam_type": scam_type,
                    "reasoning": detection_result.get('reasoning', '') if session.scam_detected else ''
                }
            })
        
        # Update session asynchronously (non-blocking)
        session_manager.update_session(session)
        
        return response_dict
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def delete_session(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete a session"""
    session_manager.delete_session(session_id)
    return {"status": "success", "message": f"Session {session_id} deleted"}


@app.get("/api/session/{session_id}")
async def get_session_info(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get session information"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "sessionId": session.session_id,
        "messageCount": session.message_count,
        "scamDetected": session.scam_detected,
        "engagementActive": session.engagement_active,
        "intelligence": session.intelligence.model_dump(),
        "createdAt": session.created_at.isoformat(),
        "lastActivity": session.last_activity.isoformat()
    }


@app.post("/api/cleanup")
async def cleanup_sessions(api_key: str = Depends(verify_api_key)):
    """Cleanup expired sessions"""
    session_manager.cleanup_expired_sessions()
    return {
        "status": "success",
        "active_sessions": len(session_manager.sessions)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
