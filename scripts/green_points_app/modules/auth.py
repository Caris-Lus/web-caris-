"""
Authentication module for Green Points Application
Handles user registration, login, and session management
"""

import os
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USERS_FILE
from modules.utils import hash_password, verify_password, generate_id, get_timestamp


class AuthManager:
    """Manages user authentication"""
    
    def __init__(self):
        self.current_user = None
    
    def register(self, username: str, password: str, email: str) -> dict:
        """
        Register a new user
        Returns: {'success': bool, 'message': str}
        """
        # Validate inputs
        if not username or len(username) < 3:
            return {'success': False, 'message': 'Username must be at least 3 characters'}
        
        if not password or len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}
        
        if not email or '@' not in email:
            return {'success': False, 'message': 'Please enter a valid email'}
        
        # Check if username already exists
        df = pd.read_csv(USERS_FILE)
        if username.lower() in df['username'].str.lower().values:
            return {'success': False, 'message': 'Username already exists'}
        
        if email.lower() in df['email'].str.lower().values:
            return {'success': False, 'message': 'Email already registered'}
        
        # Create new user
        new_user = {
            'user_id': generate_id(),
            'username': username,
            'password_hash': hash_password(password),
            'email': email,
            'is_admin': False,
            'total_points': 0,
            'total_co2_saved': 0.0,
            'created_at': get_timestamp()
        }
        
        # Append to CSV
        pd.DataFrame([new_user]).to_csv(USERS_FILE, mode='a', header=False, index=False)
        
        return {'success': True, 'message': 'Registration successful! Please login.'}
    
    def login(self, username: str, password: str) -> dict:
        """
        Login user
        Returns: {'success': bool, 'message': str, 'user': dict or None}
        """
        if not username or not password:
            return {'success': False, 'message': 'Please enter username and password', 'user': None}
        
        df = pd.read_csv(USERS_FILE)
        user_row = df[df['username'].str.lower() == username.lower()]
        
        if user_row.empty:
            return {'success': False, 'message': 'User not found', 'user': None}
        
        user = user_row.iloc[0]
        
        if not verify_password(password, user['password_hash']):
            return {'success': False, 'message': 'Incorrect password', 'user': None}
        
        # Set current user
        self.current_user = {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': bool(user['is_admin']),
            'total_points': int(user['total_points']),
            'total_co2_saved': float(user['total_co2_saved'])
        }
        
        return {'success': True, 'message': 'Login successful!', 'user': self.current_user}
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self) -> dict:
        """Get current logged in user"""
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_user is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_user and self.current_user.get('is_admin', False)
    
    def update_user_points(self, user_id: str, points_to_add: int, co2_to_add: float = 0):
        """Update user's total points and CO2 saved"""
        df = pd.read_csv(USERS_FILE)
        user_idx = df[df['user_id'] == user_id].index
        
        if not user_idx.empty:
            idx = user_idx[0]
            df.at[idx, 'total_points'] = int(df.at[idx, 'total_points']) + points_to_add
            df.at[idx, 'total_co2_saved'] = float(df.at[idx, 'total_co2_saved']) + co2_to_add
            df.to_csv(USERS_FILE, index=False)
            
            # Update current user if same
            if self.current_user and self.current_user['user_id'] == user_id:
                self.current_user['total_points'] += points_to_add
                self.current_user['total_co2_saved'] += co2_to_add
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get user statistics"""
        df = pd.read_csv(USERS_FILE)
        user_row = df[df['user_id'] == user_id]
        
        if user_row.empty:
            return None
        
        user = user_row.iloc[0]
        return {
            'username': user['username'],
            'total_points': int(user['total_points']),
            'total_co2_saved': float(user['total_co2_saved']),
            'member_since': user['created_at']
        }
    
    def get_all_users(self) -> list:
        """Get all users (for admin)"""
        df = pd.read_csv(USERS_FILE)
        users = []
        for _, row in df.iterrows():
            users.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'email': row['email'],
                'is_admin': bool(row['is_admin']),
                'total_points': int(row['total_points']),
                'total_co2_saved': float(row['total_co2_saved'])
            })
        return users
