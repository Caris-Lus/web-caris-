"""
Utility functions for Green Points Application
"""

import hashlib
import uuid
from datetime import datetime
import os
import pandas as pd
import numpy as np

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    USERS_FILE, TRANSACTIONS_FILE, PENDING_APPROVALS_FILE, 
    LOCATIONS_FILE, DATA_DIR
)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())[:8]


def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date() -> str:
    """Get current date as string"""
    return datetime.now().strftime("%Y-%m-%d")


def initialize_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    
    # Users CSV
    if not os.path.exists(USERS_FILE):
        users_df = pd.DataFrame(columns=[
            'user_id', 'username', 'password_hash', 'email', 
            'is_admin', 'total_points', 'total_co2_saved', 'created_at'
        ])
        users_df.to_csv(USERS_FILE, index=False)
        
        # Create default admin account
        admin_data = {
            'user_id': 'admin001',
            'username': 'admin',
            'password_hash': hash_password('admin123'),
            'email': 'admin@greenpoints.com',
            'is_admin': True,
            'total_points': 0,
            'total_co2_saved': 0.0,
            'created_at': get_timestamp()
        }
        pd.DataFrame([admin_data]).to_csv(USERS_FILE, mode='a', header=False, index=False)
    
    # Transactions CSV
    if not os.path.exists(TRANSACTIONS_FILE):
        transactions_df = pd.DataFrame(columns=[
            'transaction_id', 'user_id', 'activity_type', 'category',
            'points', 'co2_saved', 'details', 'timestamp', 'status'
        ])
        transactions_df.to_csv(TRANSACTIONS_FILE, index=False)
    
    # Pending Approvals CSV
    if not os.path.exists(PENDING_APPROVALS_FILE):
        approvals_df = pd.DataFrame(columns=[
            'approval_id', 'user_id', 'username', 'activity_type', 'category',
            'points', 'image_path', 'submitted_at', 'status'
        ])
        approvals_df.to_csv(PENDING_APPROVALS_FILE, index=False)
    
    # Locations CSV with sample Indian cities
    if not os.path.exists(LOCATIONS_FILE):
        locations_data = [
            {'location_name': 'Mumbai Central', 'latitude': 18.9712, 'longitude': 72.8197},
            {'location_name': 'Bandra', 'latitude': 19.0596, 'longitude': 72.8295},
            {'location_name': 'Andheri', 'latitude': 19.1136, 'longitude': 72.8697},
            {'location_name': 'Thane', 'latitude': 19.2183, 'longitude': 72.9781},
            {'location_name': 'Navi Mumbai', 'latitude': 19.0330, 'longitude': 73.0297},
            {'location_name': 'Dadar', 'latitude': 19.0178, 'longitude': 72.8478},
            {'location_name': 'Churchgate', 'latitude': 18.9322, 'longitude': 72.8264},
            {'location_name': 'Colaba', 'latitude': 18.9067, 'longitude': 72.8147},
            {'location_name': 'Borivali', 'latitude': 19.2307, 'longitude': 72.8567},
            {'location_name': 'Kandivali', 'latitude': 19.2047, 'longitude': 72.8521},
            {'location_name': 'Malad', 'latitude': 19.1874, 'longitude': 72.8484},
            {'location_name': 'Goregaon', 'latitude': 19.1663, 'longitude': 72.8526},
            {'location_name': 'Jogeshwari', 'latitude': 19.1358, 'longitude': 72.8499},
            {'location_name': 'Vile Parle', 'latitude': 19.0968, 'longitude': 72.8494},
            {'location_name': 'Santacruz', 'latitude': 19.0827, 'longitude': 72.8415},
            {'location_name': 'Kurla', 'latitude': 19.0726, 'longitude': 72.8845},
            {'location_name': 'Ghatkopar', 'latitude': 19.0858, 'longitude': 72.9080},
            {'location_name': 'Mulund', 'latitude': 19.1726, 'longitude': 72.9563},
            {'location_name': 'Powai', 'latitude': 19.1176, 'longitude': 72.9060},
            {'location_name': 'Chembur', 'latitude': 19.0522, 'longitude': 72.8994},
        ]
        pd.DataFrame(locations_data).to_csv(LOCATIONS_FILE, index=False)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)


def get_locations_list() -> list:
    """Get list of all location names"""
    if os.path.exists(LOCATIONS_FILE):
        df = pd.read_csv(LOCATIONS_FILE)
        return df['location_name'].tolist()
    return []


def get_location_coordinates(location_name: str) -> tuple:
    """Get coordinates for a location"""
    if os.path.exists(LOCATIONS_FILE):
        df = pd.read_csv(LOCATIONS_FILE)
        location = df[df['location_name'].str.lower() == location_name.lower()]
        if not location.empty:
            return (location.iloc[0]['latitude'], location.iloc[0]['longitude'])
    return None


def find_closest_location(search_term: str) -> str:
    """Find closest matching location name"""
    locations = get_locations_list()
    search_lower = search_term.lower()
    
    # Exact match
    for loc in locations:
        if loc.lower() == search_lower:
            return loc
    
    # Partial match
    for loc in locations:
        if search_lower in loc.lower() or loc.lower() in search_lower:
            return loc
    
    return None


def format_points(points: int) -> str:
    """Format points with commas"""
    return f"{points:,}"


def format_co2(co2_grams: float) -> str:
    """Format CO2 in appropriate units"""
    if co2_grams >= 1000:
        return f"{co2_grams/1000:.2f} kg"
    return f"{co2_grams:.0f} g"


def calculate_rupees(points: int) -> float:
    """Calculate rupee value from points"""
    from config import POINTS_PER_RUPEE
    return points / POINTS_PER_RUPEE
