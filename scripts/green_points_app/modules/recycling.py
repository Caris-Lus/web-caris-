"""
Recycling module for Green Points Application
Handles waste recycling submissions
"""

import os
import shutil
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import POINTS_CONFIG, PENDING_APPROVALS_FILE, UPLOADS_DIR
from modules.utils import generate_id, get_timestamp


class RecyclingManager:
    """Manages recycling submissions"""
    
    def __init__(self):
        self.waste_categories = {
            'electronic': {
                'name': 'Electronic Waste',
                'description': 'Computers, phones, TVs, batteries, cables',
                'points': POINTS_CONFIG['recycling']['electronic'],
                'examples': ['Old phones', 'Laptops', 'Batteries', 'Chargers', 'Circuit boards']
            },
            'biomedical': {
                'name': 'Biomedical Waste',
                'description': 'Medical supplies, expired medicines',
                'points': POINTS_CONFIG['recycling']['biomedical'],
                'examples': ['Expired medicines', 'Syringes', 'Bandages', 'Medical equipment']
            },
            'electrical': {
                'name': 'Electrical Waste',
                'description': 'Appliances, wires, electrical equipment',
                'points': POINTS_CONFIG['recycling']['electrical'],
                'examples': ['Fans', 'Mixers', 'Wires', 'Light bulbs', 'Motors']
            },
            'thermocol': {
                'name': 'Thermocol/Plastic',
                'description': 'Thermocol packaging, plastic containers',
                'points': POINTS_CONFIG['recycling']['thermocol'],
                'examples': ['Packaging material', 'Plastic bottles', 'Food containers', 'Thermocol sheets']
            }
        }
    
    def get_categories(self) -> dict:
        """Get all waste categories"""
        return self.waste_categories
    
    def get_category_info(self, category: str) -> dict:
        """Get information about a specific category"""
        return self.waste_categories.get(category)
    
    def submit_recycling(self, user_id: str, username: str, category: str, 
                         image_path: str) -> dict:
        """
        Submit recycling for approval
        Returns: {'success': bool, 'message': str}
        """
        if category not in self.waste_categories:
            return {'success': False, 'message': 'Invalid waste category'}
        
        if not image_path or not os.path.exists(image_path):
            return {'success': False, 'message': 'Please select a valid image'}
        
        # Copy image to uploads folder
        approval_id = generate_id()
        file_ext = os.path.splitext(image_path)[1]
        new_filename = f"recycling_{approval_id}{file_ext}"
        new_path = os.path.join(UPLOADS_DIR, new_filename)
        
        try:
            shutil.copy(image_path, new_path)
        except Exception as e:
            return {'success': False, 'message': f'Error saving image: {str(e)}'}
        
        # Create approval record
        category_info = self.waste_categories[category]
        approval = {
            'approval_id': approval_id,
            'user_id': user_id,
            'username': username,
            'activity_type': 'recycling',
            'category': category,
            'points': category_info['points'],
            'image_path': new_path,
            'submitted_at': get_timestamp(),
            'status': 'pending'
        }
        
        # Save to CSV
        pd.DataFrame([approval]).to_csv(PENDING_APPROVALS_FILE, mode='a', header=False, index=False)
        
        return {
            'success': True,
            'message': f"Recycling submission received! Pending admin approval for {category_info['points']} points.",
            'approval_id': approval_id
        }
    
    def get_user_submissions(self, user_id: str) -> list:
        """Get all recycling submissions for a user"""
        df = pd.read_csv(PENDING_APPROVALS_FILE)
        user_submissions = df[(df['user_id'] == user_id) & (df['activity_type'] == 'recycling')]
        
        submissions = []
        for _, row in user_submissions.iterrows():
            submissions.append({
                'approval_id': row['approval_id'],
                'category': row['category'],
                'points': int(row['points']),
                'submitted_at': row['submitted_at'],
                'status': row['status']
            })
        
        return submissions
