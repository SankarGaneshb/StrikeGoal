# StrikeGoal Configuration Module
import os
from pathlib import Path

# Application Settings
APP_NAME = "StrikeGoal"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Smart exam planner for Indian entrance exams"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UTILS_DIR = BASE_DIR / "utils"

# Exam Configuration
EXAM_CATEGORIES = {
    "National": ["JEE-Main", "JEE-Advanced", "NEET", "CUET"],
    "State": ["KCET", "MHT-CET", "WBJEE", "BCECE"],
    "Other": ["GMAT", "GRE", "IELTS"]
}

# Subject weights for study planning
SUBJECT_WEIGHTS = {
    "Physics": 1.0,
    "Chemistry": 0.9,
    "Biology": 0.8,
    "Mathematics": 1.1,
    "English": 0.7
}

# Study Plan Settings
DEFAULT_DAILY_HOURS = 4
DEFAULT_TARGET_SCORE = 75
MIN_STUDY_HOURS = 1
MAX_STUDY_HOURS = 12

# Google Calendar Settings
GOOGLE_CALENDAR_ENABLED = False
CALENDAR_ID = "primary"
NOTIFICATION_DAYS_BEFORE = 1

# Notification Settings
NOTIFICATION_ENABLED = True
NOTIFICATION_TIME = "09:00"  # 9 AM IST
TIMEZONE = "Asia/Kolkata"

# UI Theme
THEME = {
    "primaryColor": "#667eea",
    "backgroundColor": "#ffffff",
    "secondaryBackgroundColor": "#f0f2f6",
    "textColor": "#262730",
    "font": "sans serif"
}

# Feature Flags
FEATURES = {
    "google_calendar_sync": False,
    "auto_update_exams": False,
    "study_planner": True,
    "analytics": True,
    "notifications": True
}

# Debug Mode
DEBUG = os.getenv("STRIKEGOAL_DEBUG", "false").lower() == "true"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "strikegoal.log"

# API Keys (should be set via environment variables)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY", "")

def get_config():
    """Return the current configuration dictionary."""
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "debug": DEBUG,
        "timezone": TIMEZONE,
        "features": FEATURES,
        "exam_categories": EXAM_CATEGORIES,
        "subject_weights": SUBJECT_WEIGHTS,
        "theme": THEME
    }
