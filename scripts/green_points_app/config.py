"""
Configuration constants for Green Points Application
"""

import os

# Application Settings
APP_NAME = "Green Points - CO2 Tracker"
APP_VERSION = "1.0.0"

# Window Settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_BG = "#f0f4f0"

# Colors
PRIMARY_COLOR = "#2e7d32"  # Green
SECONDARY_COLOR = "#4caf50"  # Light Green
ACCENT_COLOR = "#81c784"  # Lighter Green
ERROR_COLOR = "#d32f2f"  # Red
WARNING_COLOR = "#ff9800"  # Orange
SUCCESS_COLOR = "#388e3c"  # Dark Green
TEXT_COLOR = "#212121"  # Dark Gray
LIGHT_TEXT = "#ffffff"  # White
CARD_BG = "#ffffff"  # White
SIDEBAR_BG = "#1b5e20"  # Dark Green

# Fonts
FONT_FAMILY = "Helvetica"
FONT_LARGE = (FONT_FAMILY, 24, "bold")
FONT_MEDIUM = (FONT_FAMILY, 14)
FONT_SMALL = (FONT_FAMILY, 12)
FONT_BUTTON = (FONT_FAMILY, 12, "bold")
FONT_TITLE = (FONT_FAMILY, 18, "bold")

# Points Configuration
POINTS_CONFIG = {
    "transport": {
        "walking": 10,      # points per km
        "cycling": 8,       # points per km
        "public_transport": 5,  # points per km
    },
    "recycling": {
        "electronic": 50,
        "biomedical": 40,
        "electrical": 45,
        "thermocol": 30,
    },
    "drives": {
        "blood_donation": 200,
        "tree_plantation": 100,
        "beach_cleanup": 150,
    }
}

# CO2 Emissions (grams per km)
CO2_EMISSIONS = {
    "car": 120,  # Baseline
    "walking": 0,
    "cycling": 0,
    "public_transport": 50,
}

# Rewards Configuration
POINTS_PER_RUPEE = 1000  # 1000 points = 1 Rupee
MIN_REDEMPTION_POINTS = 1000

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "assets", "uploads")

# CSV File Paths
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.csv")
PENDING_APPROVALS_FILE = os.path.join(DATA_DIR, "pending_approvals.csv")
LOCATIONS_FILE = os.path.join(DATA_DIR, "locations.csv")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
