from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = ConfigDict(extra='allow')  # Allow unlimited API keys
    
    # API Configuration
    API_KEY: str
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # LLM Configuration
    LLM_PROVIDER: str = "anthropic"  # openai, anthropic, or gemini
    
    # Anthropic Configuration - Support UNLIMITED API keys
    ANTHROPIC_API_KEY: Optional[str] = None  # Primary key
    ANTHROPIC_API_KEY_2: Optional[str] = None  # Additional keys for rotation
    ANTHROPIC_API_KEY_3: Optional[str] = None
    ANTHROPIC_API_KEY_4: Optional[str] = None
    # You can add ANTHROPIC_API_KEY_5, ANTHROPIC_API_KEY_6, etc. in .env - no code changes needed!
    ANTHROPIC_MODEL: str = "claude-haiku-4.5-20250110"
    
    def get_anthropic_api_keys(self) -> List[str]:
        """Get all configured Anthropic API keys - automatically detects unlimited keys"""
        keys = []
        # Check both explicit attributes and dynamically loaded ones from model_extra
        all_attrs = set(dir(self))
        if hasattr(self, 'model_extra') and self.model_extra:
            all_attrs.update(self.model_extra.keys())
        
        for attr_name in sorted(all_attrs):
            if attr_name.startswith('ANTHROPIC_API_KEY'):
                key_value = getattr(self, attr_name, None)
                if key_value and isinstance(key_value, str) and key_value != "your-anthropic-api-key-here":
                    keys.append(key_value)
        return keys
    
    # Gemini Configuration - Support UNLIMITED API keys
    GOOGLE_API_KEY: Optional[str] = None  # Primary key
    GOOGLE_API_KEY_2: Optional[str] = None  # Additional keys for rotation
    GOOGLE_API_KEY_3: Optional[str] = None
    GOOGLE_API_KEY_4: Optional[str] = None
    # You can add GOOGLE_API_KEY_5, GOOGLE_API_KEY_6, etc. in .env - no code changes needed!
    GEMINI_MODEL: str = "gemini-pro"
    
    def get_gemini_api_keys(self) -> List[str]:
        """Get all configured Gemini API keys - automatically detects unlimited keys"""
        keys = []
        # Check both explicit attributes and dynamically loaded ones from model_extra
        all_attrs = set(dir(self))
        if hasattr(self, 'model_extra') and self.model_extra:
            all_attrs.update(self.model_extra.keys())
        
        for attr_name in sorted(all_attrs):
            if attr_name.startswith('GOOGLE_API_KEY'):
                key_value = getattr(self, attr_name, None)
                if key_value and isinstance(key_value, str) and key_value != "your-google-api-key-here" and key_value != "your-primary-gemini-key-here":
                    keys.append(key_value)
        return keys
    
    # OpenAI Configuration - Support UNLIMITED API keys
    OPENAI_API_KEY: Optional[str] = None  # Primary key
    OPENAI_API_KEY_2: Optional[str] = None  # Additional keys for rotation
    OPENAI_API_KEY_3: Optional[str] = None
    OPENAI_API_KEY_4: Optional[str] = None
    # You can add OPENAI_API_KEY_5, OPENAI_API_KEY_6, etc. in .env - no code changes needed!
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    def get_openai_api_keys(self) -> List[str]:
        """Get all configured OpenAI API keys - automatically detects unlimited keys"""
        keys = []
        # Check both explicit attributes and dynamically loaded ones from model_extra
        all_attrs = set(dir(self))
        if hasattr(self, 'model_extra') and self.model_extra:
            all_attrs.update(self.model_extra.keys())
        
        for attr_name in sorted(all_attrs):
            if attr_name.startswith('OPENAI_API_KEY'):
                key_value = getattr(self, attr_name, None)
                if key_value and isinstance(key_value, str) and key_value != "your-openai-api-key-here":
                    keys.append(key_value)
        return keys
    
    # GUVI Configuration
    GUVI_CALLBACK_URL: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # Security Configuration
    RATE_LIMIT_PER_MINUTE: int = 60  # Requests per IP per minute
    MAX_REQUEST_SIZE: int = 1048576  # 1MB max request body
    
    # Response Configuration
    INCLUDE_DEBUG_INFO: bool = False  # Set to True to include detailed debug fields in response
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_MESSAGES_PER_SESSION: int = 50
    
    # Redis Configuration (Optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    USE_REDIS: bool = False
    
    # Performance Configuration (OPTIMIZED FOR SPEED & ACCURACY)
    CACHE_MAX_SIZE: int = 1000  # Increased cache for more hits
    LLM_MAX_TOKENS_DETECTION: int = 500  # Reduced for faster detection
    LLM_MAX_TOKENS_RESPONSE: int = 150   # Reduced for faster agent responses
    LLM_TEMPERATURE_DETECTION: float = 0.1
    LLM_TEMPERATURE_RESPONSE: float = 0.7
    LLM_REQUEST_TIMEOUT: int = 5  # Fast timeout for quick failures
    
    # Fast-path optimization (bypass LLM for obvious scams)
    ENABLE_FAST_PATH: bool = True  # 10x faster for obvious scams
    FAST_PATH_THRESHOLD: int = 6   # Keyword score threshold for fast detection
    
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
    
    # Pydantic v2 configuration
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='allow'  # Allow unlimited API key variables
    )


settings = Settings()
