"""
Rewards module for Green Points Application
Handles points redemption
"""

import os
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import POINTS_PER_RUPEE, MIN_REDEMPTION_POINTS, TRANSACTIONS_FILE, USERS_FILE
from modules.utils import generate_id, get_timestamp


class RewardsManager:
    """Manages rewards and redemption"""
    
    def __init__(self):
        self.points_per_rupee = POINTS_PER_RUPEE
        self.min_redemption = MIN_REDEMPTION_POINTS
    
    def get_redemption_info(self) -> dict:
        """Get redemption rate information"""
        return {
            'points_per_rupee': self.points_per_rupee,
            'min_redemption_points': self.min_redemption,
            'rate_display': f"{self.points_per_rupee} points = Rs. 1"
        }
    
    def calculate_rupee_value(self, points: int) -> float:
        """Calculate rupee value for given points"""
        return points / self.points_per_rupee
    
    def can_redeem(self, user_points: int, requested_points: int) -> tuple:
        """
        Check if user can redeem points
        Returns: (can_redeem: bool, message: str)
        """
        if requested_points < self.min_redemption:
            return (False, f"Minimum redemption is {self.min_redemption} points")
        
        if requested_points > user_points:
            return (False, f"Insufficient points. You have {user_points} points")
        
        if requested_points % self.points_per_rupee != 0:
            return (False, f"Redemption must be in multiples of {self.points_per_rupee}")
        
        return (True, "Eligible for redemption")
    
    def redeem_points(self, user_id: str, points_to_redeem: int) -> dict:
        """
        Redeem points for rupees
        Returns: {'success': bool, 'rupees': float, 'message': str}
        """
        # Get user's current points
        users_df = pd.read_csv(USERS_FILE)
        user_idx = users_df[users_df['user_id'] == user_id].index
        
        if user_idx.empty:
            return {'success': False, 'message': 'User not found'}
        
        idx = user_idx[0]
        current_points = int(users_df.at[idx, 'total_points'])
        
        # Validate redemption
        can_redeem, message = self.can_redeem(current_points, points_to_redeem)
        if not can_redeem:
            return {'success': False, 'message': message}
        
        # Calculate rupees
        rupees = self.calculate_rupee_value(points_to_redeem)
        
        # Deduct points
        users_df.at[idx, 'total_points'] = current_points - points_to_redeem
        users_df.to_csv(USERS_FILE, index=False)
        
        # Create transaction record
        transaction = {
            'transaction_id': generate_id(),
            'user_id': user_id,
            'activity_type': 'redemption',
            'category': 'points_to_rupees',
            'points': -points_to_redeem,
            'co2_saved': 0,
            'details': f"Redeemed {points_to_redeem} points for Rs. {rupees:.2f}",
            'timestamp': get_timestamp(),
            'status': 'completed'
        }
        pd.DataFrame([transaction]).to_csv(TRANSACTIONS_FILE, mode='a', header=False, index=False)
        
        return {
            'success': True,
            'rupees': rupees,
            'remaining_points': current_points - points_to_redeem,
            'message': f"Successfully redeemed! You will receive Rs. {rupees:.2f}"
        }
    
    def get_redemption_history(self, user_id: str) -> list:
        """Get user's redemption history"""
        df = pd.read_csv(TRANSACTIONS_FILE)
        redemptions = df[(df['user_id'] == user_id) & (df['activity_type'] == 'redemption')]
        
        history = []
        for _, row in redemptions.iterrows():
            history.append({
                'transaction_id': row['transaction_id'],
                'points': abs(int(row['points'])),
                'rupees': abs(int(row['points'])) / self.points_per_rupee,
                'details': row['details'],
                'timestamp': row['timestamp']
            })
        
        return history
    
    def get_available_redemption_options(self, user_points: int) -> list:
        """Get available redemption options based on user's points"""
        options = []
        
        # Generate options in increments of points_per_rupee
        for multiplier in [1, 2, 5, 10, 20, 50, 100]:
            points_needed = multiplier * self.points_per_rupee
            if points_needed <= user_points:
                options.append({
                    'points': points_needed,
                    'rupees': multiplier,
                    'display': f"{points_needed:,} points = Rs. {multiplier}"
                })
        
        return options
