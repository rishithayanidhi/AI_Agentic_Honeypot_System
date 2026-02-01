from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class Message(BaseModel):
    """Represents a single message in the conversation"""
    sender: str  # "scammer" or "user"
    text: str
    timestamp: Union[str, int]  # Accept both string and integer timestamps
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def convert_timestamp(cls, v):
        """Convert integer timestamp to ISO string format"""
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
    session_id: Optional[str] = Field(default="test-session", alias="sessionId")
    message: Optional[str] = Field(default="Hello, this is a test message")
    
    class Config:
        populate_by_name = True  # Allow both session_id and sessionId


class IncomingRequest(BaseModel):
    """Full incoming API request structure"""
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from the scammer"""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


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
