from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
from typing import Optional, Union

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

# Initialize FastAPI app
app = FastAPI(
    title="AI Agentic Honeypot System",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Agentic Honeypot System",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
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
        # Handle both request formats
        if isinstance(request, SimpleIncomingRequest):
            # Convert simple format to full format
            session_id = request.session_id
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
        
        # Add incoming message to session
        session.messages.append(message_obj)
        session.message_count += 1
        
        # Add conversation history to session if this is first message
        if conversation_history and not session.engagement_active:
            for hist_msg in conversation_history:
                if hist_msg not in session.messages:
                    session.messages.insert(0, hist_msg)
        
        # Extract intelligence from current message
        new_intel = intelligence_extractor.extract_from_message(message_text)
        session.intelligence = intelligence_extractor.merge_intelligence(
            session.intelligence, new_intel
        )
        
        # Initialize detection variables
        detection_result = {}
        scam_confidence = 0.0
        scam_type = 'unknown'
        
        # Detect scam if not already detected
        if not session.scam_detected:
            try:
                detection_result = scam_detector.detect_scam(
                    message_text,
                    session.messages
                )
                
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
            except Exception as detect_error:
                logger.error(f"Error in scam detection: {detect_error}", exc_info=True)
                detection_result = {
                    'is_scam': False,
                    'confidence': 0.0,
                    'scam_type': 'error',
                    'reasoning': f'Detection error: {str(detect_error)[:100]}'
                }
                session.scam_detected = False
                scam_confidence = 0.0
                scam_type = 'error'
            
            logger.info(f"Scam detection: {session.scam_detected} (confidence: {scam_confidence})")
            
            if session.scam_detected:
                session.engagement_active = True
                session.agent_notes = f"Scam detected: {scam_type}. {detection_result.get('reasoning', '')}"
        else:
            # Already detected in previous message
            scam_confidence = 0.95
            scam_type = "confirmed"
            detection_result = {
                'is_scam': True,
                'confidence': 0.95,
                'scam_type': 'confirmed',
                'reasoning': session.agent_notes or 'Previously detected as scam'
            }
        
        # Generate agent response if scam is detected
        agent_response_text = None
        session_complete = False
        
        if session.scam_detected and session.engagement_active:
            try:
                # Select or maintain persona
                if not session.persona or session.message_count % 5 == 0:
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
        
        # Calculate engagement duration
        engagement_duration = int((datetime.now() - session.created_at).total_seconds())
        
        # Prepare intelligence in both formats
        intel_camel = session.intelligence.model_dump()
        intel_snake = {
            "phone_numbers": session.intelligence.phoneNumbers,
            "upi_ids": session.intelligence.upiIds,
            "links": session.intelligence.phishingLinks,
            "keywords": session.intelligence.suspiciousKeywords,
            "bank_accounts": session.intelligence.bankAccounts
        }
        
        # Prepare response (includes both camelCase and snake_case for compatibility)
        response_dict = {
            "status": "success",
            "scamDetected": session.scam_detected,
            "agentResponse": agent_response_text,
            "engagementMetrics": {
                "engagementDurationSeconds": engagement_duration,
                "totalMessagesExchanged": session.message_count
            },
            "extractedIntelligence": intel_camel,
            "agentNotes": session.agent_notes,
            "sessionComplete": session_complete,
            # Add snake_case aliases for test compatibility
            "detection": {
                "is_scam": session.scam_detected,
                "confidence": scam_confidence,
                "scam_type": scam_type,
                "reasoning": detection_result.get('reasoning', '') if session.scam_detected else ''
            },
            "response": agent_response_text,
            "intelligence_extracted": intel_snake  # Use snake_case version for tests
        }
        
        response = APIResponse(
            status="success",
            scamDetected=session.scam_detected,
            agentResponse=agent_response_text,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=engagement_duration,
                totalMessagesExchanged=session.message_count
            ),
            extractedIntelligence=session.intelligence,
            agentNotes=session.agent_notes,
            sessionComplete=session_complete
        )
        
        # Update session
        session_manager.update_session(session)
        
        # Clean up if session is complete
        if session_complete:
            # Keep session for a bit for debugging, but mark as inactive
            pass
        
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
