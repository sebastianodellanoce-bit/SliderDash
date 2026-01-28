"""Configuration settings for the Google Analytics Dashboard."""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load .env from config folder (for local development)
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


def get_secret(key: str, default: str = "") -> str:
    """Get secret from Streamlit secrets (cloud) or environment variable (local)."""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    # Fall back to environment variable (for local development)
    return os.getenv(key, default)


# Google Analytics 4 configuration
GA_PROPERTY_ID = get_secret("GA_PROPERTY_ID", "")
GA_CREDENTIALS_PATH = os.getenv("GA_CREDENTIALS_PATH", "")  # Only for local file-based auth
USE_DEFAULT_CREDENTIALS = get_secret("USE_DEFAULT_CREDENTIALS", "false").lower() == "true"

# Claude AI configuration
ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY", "")

# Dashboard settings
PAGE_TITLE = "Slider Steps Report"
PAGE_ICON = "assets/enpal-icon.png"
LAYOUT = "wide"

# Date format
DATE_FORMAT = "%d/%m/%Y"
DATE_FORMAT_INTERNAL = "%Y-%m-%d"

# GA4 Data Settings
GA4_ROW_LIMIT = 500000  # Increased from 250k to reduce data truncation
GA4_DATE_RANGE_DAYS = 90  # Days of data to fetch
GA4_TIMEZONE = "Europe/Rome"  # Timezone for date calculations

# Cache settings
CACHE_TTL_SECONDS = 1800  # 30 minutes (reduced from 1 hour)
