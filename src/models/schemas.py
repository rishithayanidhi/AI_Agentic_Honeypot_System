from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class Message(BaseModel):
    """Represents a single message in the conversation.
    
    Attributes:
        sender: Message sender ('scammer' or 'user')
        text: Message content
        timestamp: Message timestamp (ISO format string or Unix epoch ms)
    """
    sender: Optional[str] = Field(default="scammer", description="Message sender")
    text: Optional[str] = Field(default="", description="Message content")
    timestamp: Optional[Union[str, int]] = Field(default=None, description="Message timestamp")
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def convert_timestamp(cls, v: Optional[Union[str, int]]) -> str:
        """Convert integer timestamp to ISO string format.
        
        Args:
            v: Timestamp value (string, int, or None)
            
        Returns:
            ISO format timestamp string
        """
        if v is None:
            return datetime.now().isoformat()
        if isinstance(v, int):
            # Convert milliseconds timestamp to ISO format
            return datetime.fromtimestamp(v / 1000).isoformat()
        return v


class Metadata(BaseModel):
    """Additional metadata about the conversation"""
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class EmptyRequest(BaseModel):
    """Accepts completely empty body for GUVI endpoint tester"""
    pass


class SimpleIncomingRequest(BaseModel):
    """Simplified incoming API request structure (for testing)"""
    session_id: Optional[str] = Field(default=None, alias="sessionId")
    message: Optional[Union[str, Dict[str, Any]]] = Field(default=None)  # Accept both string and dict
    conversationHistory: Optional[List[Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        populate_by_name = True  # Allow both session_id and sessionId


class IncomingRequest(BaseModel):
    """Full incoming API request structure"""
    sessionId: Optional[str] = None
    message: Optional[Union[Message, str, Dict[str, Any]]] = None  # Accept Message object, string, or dict
    conversationHistory: Optional[List[Any]] = Field(default_factory=list)  # Accept any format
    metadata: Optional[Union[Metadata, Dict[str, Any]]] = None  # Accept Metadata or dict
    
    class Config:
        populate_by_name = True


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from scammer conversations.
    
    All fields are lists to support multiple extracted values.
    Ordered by evaluation importance (highest score first).
    
    Attributes:
        phoneNumbers: Extracted phone numbers (10 points)
        bankAccounts: Extracted bank account numbers (10 points)
        upiIds: Extracted UPI IDs (10 points)
        phishingLinks: Extracted suspicious URLs (10 points)
        emailAddresses: Extracted email addresses (10 points)
        suspiciousKeywords: Scam-related keywords (for analysis)
    """
    phoneNumbers: List[str] = Field(default_factory=list, description="Phone numbers")
    bankAccounts: List[str] = Field(default_factory=list, description="Bank account numbers")
    upiIds: List[str] = Field(default_factory=list, description="UPI IDs")
    phishingLinks: List[str] = Field(default_factory=list, description="Phishing URLs")
    emailAddresses: List[str] = Field(default_factory=list, description="Email addresses")
    suspiciousKeywords: List[str] = Field(default_factory=list, description="Scam keywords")


class EngagementMetrics(BaseModel):
    """Metrics about the engagement"""
    engagementDurationSeconds: int = 0
    totalMessagesExchanged: int = 0


class APIResponse(BaseModel):
    """API response structure"""
    status: str = "success"
    scamDetected: bool
    agentResponse: Optional[str] = None  # The response to send back to scammer
    engagementMetrics: Optional[EngagementMetrics] = None
    extractedIntelligence: Optional[ExtractedIntelligence] = None
    agentNotes: Optional[str] = None
    sessionComplete: bool = False  # Whether the conversation has ended


class GUVICallbackPayload(BaseModel):
    """Payload to send to GUVI evaluation endpoint"""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: Dict[str, Any]
    agentNotes: str
