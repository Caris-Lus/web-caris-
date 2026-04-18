"""
Admin module for Green Points Application
Handles approval/rejection of submissions
"""

import os
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PENDING_APPROVALS_FILE, TRANSACTIONS_FILE, USERS_FILE
from modules.utils import generate_id, get_timestamp


class AdminManager:
    """Manages admin operations"""
    
    def get_pending_approvals(self) -> list:
        """Get all pending approval requests"""
        df = pd.read_csv(PENDING_APPROVALS_FILE)
        pending = df[df['status'] == 'pending']
        
        approvals = []
        for _, row in pending.iterrows():
            approvals.append({
                'approval_id': row['approval_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'activity_type': row['activity_type'],
                'category': row['category'],
                'points': int(row['points']),
                'image_path': row['image_path'],
                'submitted_at': row['submitted_at']
            })
        
        return approvals
    
    def approve_submission(self, approval_id: str) -> dict:
        """
        Approve a submission and award points
        Returns: {'success': bool, 'message': str}
        """
        # Read approvals file
        approvals_df = pd.read_csv(PENDING_APPROVALS_FILE)
        approval_idx = approvals_df[approvals_df['approval_id'] == approval_id].index
        
        if approval_idx.empty:
            return {'success': False, 'message': 'Submission not found'}
        
        idx = approval_idx[0]
        approval = approvals_df.loc[idx]
        
        if approval['status'] != 'pending':
            return {'success': False, 'message': 'Submission already processed'}
        
        # Update approval status
        approvals_df.at[idx, 'status'] = 'approved'
        approvals_df.to_csv(PENDING_APPROVALS_FILE, index=False)
        
        # Create transaction record
        transaction = {
            'transaction_id': generate_id(),
            'user_id': approval['user_id'],
            'activity_type': approval['activity_type'],
            'category': approval['category'],
            'points': int(approval['points']),
            'co2_saved': 0,  # Non-transport activities don't track CO2
            'details': f"Approved: {approval['category']}",
            'timestamp': get_timestamp(),
            'status': 'completed'
        }
        pd.DataFrame([transaction]).to_csv(TRANSACTIONS_FILE, mode='a', header=False, index=False)
        
        # Update user points
        users_df = pd.read_csv(USERS_FILE)
        user_idx = users_df[users_df['user_id'] == approval['user_id']].index
        
        if not user_idx.empty:
            u_idx = user_idx[0]
            users_df.at[u_idx, 'total_points'] = int(users_df.at[u_idx, 'total_points']) + int(approval['points'])
            users_df.to_csv(USERS_FILE, index=False)
        
        return {
            'success': True,
            'message': f"Approved! {approval['points']} points awarded to {approval['username']}"
        }
    
    def reject_submission(self, approval_id: str, reason: str = '') -> dict:
        """
        Reject a submission
        Returns: {'success': bool, 'message': str}
        """
        # Read approvals file
        approvals_df = pd.read_csv(PENDING_APPROVALS_FILE)
        approval_idx = approvals_df[approvals_df['approval_id'] == approval_id].index
        
        if approval_idx.empty:
            return {'success': False, 'message': 'Submission not found'}
        
        idx = approval_idx[0]
        
        if approvals_df.at[idx, 'status'] != 'pending':
            return {'success': False, 'message': 'Submission already processed'}
        
        # Update approval status
        approvals_df.at[idx, 'status'] = 'rejected'
        approvals_df.to_csv(PENDING_APPROVALS_FILE, index=False)
        
        return {
            'success': True,
            'message': 'Submission rejected'
        }
    
    def get_all_users_stats(self) -> list:
        """Get statistics for all users"""
        users_df = pd.read_csv(USERS_FILE)
        
        stats = []
        for _, row in users_df.iterrows():
            stats.append({
                'username': row['username'],
                'email': row['email'],
                'total_points': int(row['total_points']),
                'total_co2_saved': float(row['total_co2_saved']),
                'is_admin': bool(row['is_admin'])
            })
        
        # Sort by points descending
        stats.sort(key=lambda x: x['total_points'], reverse=True)
        return stats
    
    def get_submission_stats(self) -> dict:
        """Get overall submission statistics"""
        approvals_df = pd.read_csv(PENDING_APPROVALS_FILE)
        
        return {
            'total_submissions': len(approvals_df),
            'pending': len(approvals_df[approvals_df['status'] == 'pending']),
            'approved': len(approvals_df[approvals_df['status'] == 'approved']),
            'rejected': len(approvals_df[approvals_df['status'] == 'rejected'])
        }
