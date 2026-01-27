from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_KEY: str
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # LLM Configuration
    LLM_PROVIDER: str = "gemini"  # openai, anthropic, or gemini
    
    # Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # GUVI Configuration
    GUVI_CALLBACK_URL: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_MESSAGES_PER_SESSION: int = 50
    
    # Redis Configuration (Optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    USE_REDIS: bool = False
    
    # Performance Configuration (OPTIMIZED FOR SPEED)
    CACHE_MAX_SIZE: int = 500  # Increased cache for more hits
    LLM_MAX_TOKENS_DETECTION: int = 300  # Reduced for speed
    LLM_MAX_TOKENS_RESPONSE: int = 150   # Reduced for speed
    LLM_TEMPERATURE_DETECTION: float = 0.1
    LLM_TEMPERATURE_RESPONSE: float = 0.7
    LLM_REQUEST_TIMEOUT: int = 5  # Reduced timeout for faster failures
    
    # Detection Configuration (Dynamic Thresholds)
    SCAM_DETECTION_THRESHOLD: float = 0.5  # Minimum confidence to consider as scam
    SCAM_SCORE_THRESHOLD: int = 2  # Minimum total score for scam detection
    LOTTERY_CONFIDENCE_MULTIPLIER: float = 0.3
    BANK_FRAUD_CONFIDENCE_MULTIPLIER: float = 0.25
    UPI_CONFIDENCE_MULTIPLIER: float = 0.3
    PHISHING_CONFIDENCE_MULTIPLIER: float = 0.35
    GENERIC_CONFIDENCE_MULTIPLIER: float = 0.25
    MAX_CONFIDENCE: float = 0.95
    MIN_CONFIDENCE_NOT_SCAM: float = 0.4
    
    # Conversation Configuration
    PERSONA_CHANGE_INTERVAL: int = 5  # Change persona every N messages
    EARLY_STAGE_THRESHOLD: int = 3  # Messages before mid-conversation
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
