"""Configuration settings for the Google Analytics Dashboard."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from config folder
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Google Analytics 4 configuration (only supported data source)
GA_PROPERTY_ID = os.getenv("GA_PROPERTY_ID", "")
GA_CREDENTIALS_PATH = os.getenv("GA_CREDENTIALS_PATH", "")
USE_DEFAULT_CREDENTIALS = os.getenv("USE_DEFAULT_CREDENTIALS", "false").lower() == "true"

# Dashboard settings
PAGE_TITLE = "Slider Steps Report"
PAGE_ICON = "assets/enpal-icon.png"
LAYOUT = "wide"

# Date format
DATE_FORMAT = "%d/%m/%Y"
DATE_FORMAT_INTERNAL = "%Y-%m-%d"
