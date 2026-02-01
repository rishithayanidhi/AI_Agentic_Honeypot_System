from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import asyncio
import warnings
from typing import Optional, Union

# Suppress Pydantic warnings from google-genai library
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._fields")

from config import settings
from src.models.schemas import (
    IncomingRequest, SimpleIncomingRequest, APIResponse, EngagementMetrics, 
    ExtractedIntelligence, Message
)
from src.services.session_manager import session_manager
from src.services.scam_detector import ScamDetector
from src.services.ai_agent import AIAgent
from src.utils.intelligence_extractor import IntelligenceExtractor
from src.services.guvi_callback import guvi_callback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    logger.error(f"Validation error for {request.url.path}")
    logger.error(f"Validation errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Request validation failed. Check the required fields and ensure timestamp is a valid format."
        }
    )
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
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "AI Agentic Honeypot System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_manager.sessions),
        "llm_provider": settings.LLM_PROVIDER
    }


@app.post("/api/message")
async def handle_message(
    request: Union[IncomingRequest, SimpleIncomingRequest],
    api_key: str = Depends(verify_api_key)
):
    """
    Main endpoint to handle incoming messages
    Accepts both full format (with Message object) and simple format (with string)
    """
    try:
        logger.info(f"Received request type: {type(request).__name__}")
        logger.info(f"Request data: {request.model_dump()}")
        # Handle both request formats
        if isinstance(request, SimpleIncomingRequest):
            # Convert simple format to full format
            session_id = request.session_id or f"auto-{datetime.now().timestamp()}"
            message_text = request.message
            message_obj = Message(
                sender="scammer",
                text=message_text,
                timestamp=datetime.now().isoformat()
            )
            conversation_history = []
        else:
            # Full format
            session_id = request.sessionId
            message_obj = request.message
            message_text = request.message.text
            conversation_history = request.conversationHistory
        
        logger.info(f"Received message for session: {session_id}")
        
        # Get or create session
        session = session_manager.get_or_create_session(session_id)
        
        # Early exit if session is already complete
        if not session.engagement_active and session.scam_detected:
            return {
                "status": "success",
                "scamDetected": True,
                "agentResponse": "Thank you for your message. This conversation has ended.",
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
        
        # Add conversation history to session if this is first message (only if list is small)
        if conversation_history and not session.engagement_active and len(conversation_history) < 10:
            for hist_msg in conversation_history:
                if hist_msg not in session.messages:
                    session.messages.insert(0, hist_msg)
        
        # Initialize detection variables
        detection_result = {}
        scam_confidence = 0.0
        scam_type = 'unknown'
        
        # SPEED OPTIMIZED: Run synchronously, intelligence extraction is fast
        if not session.scam_detected:
            # Extract intelligence first (fast, no API calls)
            try:
                new_intel = intelligence_extractor.extract_from_message(message_text)
                session.intelligence = intelligence_extractor.merge_intelligence(
                    session.intelligence, new_intel
                )
            except Exception as e:
                logger.error(f"Intelligence extraction error: {e}")
            
            # Scam detection (uses keyword-based fallback primarily, fast)
            try:
                detection_result = scam_detector.detect_scam(message_text, session.messages)
            except Exception as e:
                logger.error(f"Scam detection error: {e}")
                detection_result = {
                    'is_scam': False,
                    'confidence': 0.0,
                    'scam_type': 'error',
                    'reasoning': f'Detection error: {str(e)[:100]}'
                }
        else:
            # Session already detected - only extract intelligence (fast)
            new_intel = intelligence_extractor.extract_from_message(message_text)
            session.intelligence = intelligence_extractor.merge_intelligence(
                session.intelligence, new_intel
            )
        
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
                
                # Generate response with error handling
                agent_decision = ai_agent.generate_response(
                    scammer_message=message_text,
                    conversation_history=session.messages,
                    persona=session.persona,
                    scam_type=scam_type,
                    extracted_intel=session.intelligence.model_dump()
                )
                
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
                logger.info(f"Session {request.sessionId} complete: {end_reason}")
                
                # Send final results to GUVI
                success = guvi_callback.send_final_result(
                    session_id=request.sessionId,
                    scam_detected=session.scam_detected,
                    total_messages=session.message_count,
                    extracted_intelligence=session.intelligence.model_dump(),
                    agent_notes=session.agent_notes
                )
                
                if success:
                    logger.info(f"Successfully sent final results to GUVI for session {request.sessionId}")
                else:
                    logger.warning(f"Failed to send results to GUVI for session {request.sessionId}")
        
        # Fast response preparation with minimal overhead
        engagement_duration = int((datetime.now() - session.created_at).total_seconds())
        
        # Prepare response (optimized - single format conversion)
        # Optimized response dict with essential fields only
        response_dict = {
            "status": "success",
            "sessionId": session_id,
            "scamDetected": session.scam_detected,
            "isScam": session.scam_detected,
            "scamType": scam_type,
            "confidence": scam_confidence,
            "reasoning": detection_result.get('reasoning', '') if session.scam_detected else '',
            "response": agent_response_text,
            "agentResponse": agent_response_text,
            "shouldContinue": not session_complete,
            "sessionComplete": session_complete,
            "engagementMetrics": {
                "engagementDurationSeconds": engagement_duration,
                "totalMessagesExchanged": session.message_count,
                "messageCount": session.message_count,
                "engagementTime": engagement_duration,
                "scamDetectionAccuracy": scam_confidence
            },
            "extractedIntelligence": {
                "phoneNumbers": session.intelligence.phoneNumbers,
                "upiIds": session.intelligence.upiIds,
                "phishingLinks": session.intelligence.phishingLinks,
                "suspiciousKeywords": session.intelligence.suspiciousKeywords,
                "bankAccounts": session.intelligence.bankAccounts,
                # Snake_case aliases
                "phone_numbers": session.intelligence.phoneNumbers,
                "upi_ids": session.intelligence.upiIds,
                "links": session.intelligence.phishingLinks,
                "urls": session.intelligence.phishingLinks,
                "bankDetails": session.intelligence.bankAccounts,
                "bank_accounts": session.intelligence.bankAccounts,
                "keywords": session.intelligence.suspiciousKeywords
            },
            "agentNotes": session.agent_notes,
            # Compatibility fields
            "detection": {
                "is_scam": session.scam_detected,
                "confidence": scam_confidence,
                "scam_type": scam_type,
                "reasoning": detection_result.get('reasoning', '') if session.scam_detected else ''
            },
            # Add intelligence_extracted for test compatibility
            "intelligence_extracted": {
                "phone_numbers": session.intelligence.phoneNumbers,
                "upi_ids": session.intelligence.upiIds,
                "links": session.intelligence.phishingLinks,
                "urls": session.intelligence.phishingLinks,
                "bank_accounts": session.intelligence.bankAccounts,
                "keywords": session.intelligence.suspiciousKeywords
            }
        }
        
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
