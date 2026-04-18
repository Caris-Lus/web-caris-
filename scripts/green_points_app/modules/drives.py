"""
Community Drives module for Green Points Application
Handles blood donation, tree plantation, beach cleanup submissions
"""

import os
import shutil
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import POINTS_CONFIG, PENDING_APPROVALS_FILE, UPLOADS_DIR
from modules.utils import generate_id, get_timestamp


class DrivesManager:
    """Manages community drive submissions"""
    
    def __init__(self):
        self.drive_types = {
            'blood_donation': {
                'name': 'Blood Donation',
                'description': 'Donate blood and save lives',
                'points': POINTS_CONFIG['drives']['blood_donation'],
                'icon': 'Heart',
                'tips': [
                    'Take a photo of your donation certificate',
                    'Or a photo at the donation center',
                    'Include date visible if possible'
                ]
            },
            'tree_plantation': {
                'name': 'Tree Plantation',
                'description': 'Plant trees to help the environment',
                'points': POINTS_CONFIG['drives']['tree_plantation'],
                'icon': 'Tree',
                'tips': [
                    'Photo of you planting the tree',
                    'Photo of the planted sapling',
                    'Include location if possible'
                ]
            },
            'beach_cleanup': {
                'name': 'Beach Cleanup',
                'description': 'Clean beaches and protect marine life',
                'points': POINTS_CONFIG['drives']['beach_cleanup'],
                'icon': 'Beach',
                'tips': [
                    'Before and after photos work best',
                    'Photo of collected waste',
                    'Group photos from cleanup events'
                ]
            }
        }
    
    def get_drive_types(self) -> dict:
        """Get all drive types"""
        return self.drive_types
    
    def get_drive_info(self, drive_type: str) -> dict:
        """Get information about a specific drive type"""
        return self.drive_types.get(drive_type)
    
    def submit_drive(self, user_id: str, username: str, drive_type: str, 
                     image_path: str) -> dict:
        """
        Submit drive participation for approval
        Returns: {'success': bool, 'message': str}
        """
        if drive_type not in self.drive_types:
            return {'success': False, 'message': 'Invalid drive type'}
        
        if not image_path or not os.path.exists(image_path):
            return {'success': False, 'message': 'Please select a valid image as proof'}
        
        # Copy image to uploads folder
        approval_id = generate_id()
        file_ext = os.path.splitext(image_path)[1]
        new_filename = f"drive_{approval_id}{file_ext}"
        new_path = os.path.join(UPLOADS_DIR, new_filename)
        
        try:
            shutil.copy(image_path, new_path)
        except Exception as e:
            return {'success': False, 'message': f'Error saving image: {str(e)}'}
        
        # Create approval record
        drive_info = self.drive_types[drive_type]
        approval = {
            'approval_id': approval_id,
            'user_id': user_id,
            'username': username,
            'activity_type': 'drive',
            'category': drive_type,
            'points': drive_info['points'],
            'image_path': new_path,
            'submitted_at': get_timestamp(),
            'status': 'pending'
        }
        
        # Save to CSV
        pd.DataFrame([approval]).to_csv(PENDING_APPROVALS_FILE, mode='a', header=False, index=False)
        
        return {
            'success': True,
            'message': f"Drive participation submitted! Pending admin approval for {drive_info['points']} points.",
            'approval_id': approval_id
        }
    
    def get_user_submissions(self, user_id: str) -> list:
        """Get all drive submissions for a user"""
        df = pd.read_csv(PENDING_APPROVALS_FILE)
        user_submissions = df[(df['user_id'] == user_id) & (df['activity_type'] == 'drive')]
        
        submissions = []
        for _, row in user_submissions.iterrows():
            submissions.append({
                'approval_id': row['approval_id'],
                'drive_type': row['category'],
                'points': int(row['points']),
                'submitted_at': row['submitted_at'],
                'status': row['status']
            })
        
        return submissions
