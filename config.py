import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration management."""
    
    # Secret Key for Flask sessions (if needed)
    SECRET_KEY = os.getenv('SECRET_KEY', 'snjb-placement-cell-assistant-secret-key-default')
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash').strip()
    
    # Security & Input Limits
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 2000))
    MAX_DOC_SIZE_MB = int(os.getenv('MAX_DOC_SIZE_MB', 5))
    
    # Path Configurations
    KNOWLEDGE_BASE_DIR = BASE_DIR / 'knowledge_base'
    FAQS_FILE = KNOWLEDGE_BASE_DIR / 'faqs.json'
    VERIFIED_DOCS_DIR = KNOWLEDGE_BASE_DIR / 'verified_docs'
    UPLOADS_DIR = BASE_DIR / 'uploads'
    
    # College Metadata
    COLLEGE_NAME = "SNJB's Late Sau. Kantabai Bhavarlalji Jain College of Engineering"
    COLLEGE_LOCATION = "Chandwad, Nashik district, Maharashtra, India"
    COLLEGE_WEBSITE = "https://www.snjb.org/"
    APP_NAME = "SNJB Placement Cell Assistant"

    @classmethod
    def is_gemini_configured(cls) -> bool:
        """Returns True if a non-empty GEMINI_API_KEY is configured."""
        return bool(cls.GEMINI_API_KEY and len(cls.GEMINI_API_KEY) > 5)

    @classmethod
    def get_sanitized_status(cls) -> dict:
        """Returns non-sensitive status info for health endpoint."""
        has_key = cls.is_gemini_configured()
        masked_key = ""
        if has_key:
            key_len = len(cls.GEMINI_API_KEY)
            masked_key = cls.GEMINI_API_KEY[:4] + "..." + cls.GEMINI_API_KEY[-4:] if key_len >= 8 else "****"
            
        return {
            "app_name": cls.APP_NAME,
            "college_name": cls.COLLEGE_NAME,
            "gemini_configured": has_key,
            "gemini_model": cls.GEMINI_MODEL,
            "masked_key": masked_key,
            "knowledge_base_dir_exists": cls.KNOWLEDGE_BASE_DIR.exists(),
            "verified_docs_dir_exists": cls.VERIFIED_DOCS_DIR.exists(),
        }
