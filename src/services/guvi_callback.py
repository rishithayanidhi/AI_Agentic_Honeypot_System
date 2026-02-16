import requests
from typing import Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class GUVICallback:
    """Handles callbacks to GUVI evaluation endpoint"""
    
    def __init__(self):
        self.callback_url = settings.GUVI_CALLBACK_URL
    
    def send_final_result(
        self,
        session_id: str,
        scam_detected: bool,
        total_messages: int,
        extracted_intelligence: Dict[str, Any],
        agent_notes: str,
        engagement_duration: int = 0
    ) -> bool:
        """
        Send final results to GUVI evaluation endpoint
        Matches exact evaluation format for maximum score
        
        Returns: True if successful, False otherwise
        """
        
        # Prepare intelligence data - only include fields specified in evaluation
        intel_data = {
            "phoneNumbers": extracted_intelligence.get("phoneNumbers", []),
            "bankAccounts": extracted_intelligence.get("bankAccounts", []),
            "upiIds": extracted_intelligence.get("upiIds", []),
            "phishingLinks": extracted_intelligence.get("phishingLinks", []),
            "emailAddresses": extracted_intelligence.get("emailAddresses", [])
        }
        
        payload = {
            "sessionId": session_id,
            "status": "completed",  # Response structure field (2.5 points)
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intel_data,
            "engagementMetrics": {  # Optional field (2.5 points)
                "totalMessagesExchanged": total_messages,
                "engagementDurationSeconds": engagement_duration
            },
            "agentNotes": agent_notes
        }
        
        try:
            logger.info(f"Sending final result to GUVI for session {session_id}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(
                self.callback_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent results for session {session_id}")
                return True
            else:
                logger.error(f"GUVI callback failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"GUVI callback timeout for session {session_id}")
            return False
        except Exception as e:
            logger.error(f"Error sending GUVI callback: {e}")
            return False
    
    def format_intelligence_for_callback(self, intelligence: Any) -> Dict[str, Any]:
        """Format extracted intelligence for GUVI callback"""
        if hasattr(intelligence, 'model_dump'):
            return intelligence.model_dump()
        elif hasattr(intelligence, 'dict'):
            return intelligence.dict()
        else:
            return {
                "phoneNumbers": intelligence.phoneNumbers if hasattr(intelligence, 'phoneNumbers') else [],
                "bankAccounts": intelligence.bankAccounts if hasattr(intelligence, 'bankAccounts') else [],
                "upiIds": intelligence.upiIds if hasattr(intelligence, 'upiIds') else [],
                "phishingLinks": intelligence.phishingLinks if hasattr(intelligence, 'phishingLinks') else [],
                "emailAddresses": intelligence.emailAddresses if hasattr(intelligence, 'emailAddresses') else []
            }


# Global callback handler
guvi_callback = GUVICallback()
