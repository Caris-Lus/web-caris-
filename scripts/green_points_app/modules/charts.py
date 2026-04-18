"""
Charts module for Green Points Application
Handles data visualization using Matplotlib and Seaborn
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TRANSACTIONS_FILE, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR


class ChartsManager:
    """Manages chart generation and display"""
    
    def __init__(self):
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 10
        
        # Color palette
        self.colors = {
            'primary': PRIMARY_COLOR,
            'secondary': SECONDARY_COLOR,
            'accent': ACCENT_COLOR,
            'transport': '#4CAF50',
            'recycling': '#2196F3',
            'drives': '#FF9800',
            'redemption': '#F44336'
        }
    
    def get_user_transactions(self, user_id: str) -> pd.DataFrame:
        """Get all transactions for a user"""
        if not os.path.exists(TRANSACTIONS_FILE):
            return pd.DataFrame()
        
        df = pd.read_csv(TRANSACTIONS_FILE)
        user_df = df[df['user_id'] == user_id].copy()
        
        if not user_df.empty:
            user_df['timestamp'] = pd.to_datetime(user_df['timestamp'])
            user_df = user_df.sort_values('timestamp')
        
        return user_df
    
    def create_co2_savings_chart(self, user_id: str, parent_frame) -> FigureCanvasTkAgg:
        """
        Create line chart showing CO2 savings over time
        Returns: FigureCanvasTkAgg object to embed in Tkinter
        """
        df = self.get_user_transactions(user_id)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#f0f4f0')
        ax.set_facecolor('#ffffff')
        
        if df.empty or df['co2_saved'].sum() == 0:
            # No data - show placeholder
            ax.text(0.5, 0.5, 'No CO2 savings data yet!\nStart using eco-friendly transport.',
                   ha='center', va='center', fontsize=12, color='gray',
                   transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        else:
            # Filter transport transactions (they have CO2 data)
            transport_df = df[df['co2_saved'] > 0].copy()
            
            if not transport_df.empty:
                # Group by date and sum CO2 saved
                transport_df['date'] = transport_df['timestamp'].dt.date
                daily_co2 = transport_df.groupby('date')['co2_saved'].sum().reset_index()
                daily_co2['cumulative_co2'] = daily_co2['co2_saved'].cumsum()
                
                # Plot
                ax.fill_between(range(len(daily_co2)), daily_co2['cumulative_co2'], 
                               alpha=0.3, color=self.colors['primary'])
                ax.plot(range(len(daily_co2)), daily_co2['cumulative_co2'], 
                       color=self.colors['primary'], linewidth=2, marker='o', markersize=6)
                
                # Labels
                ax.set_xlabel('Days', fontsize=11)
                ax.set_ylabel('Total CO2 Saved (grams)', fontsize=11)
                
                # Format y-axis for large numbers
                if daily_co2['cumulative_co2'].max() > 1000:
                    ax.set_ylabel('Total CO2 Saved (kg)', fontsize=11)
                    ax.set_yticklabels([f'{y/1000:.1f}' for y in ax.get_yticks()])
            else:
                ax.text(0.5, 0.5, 'No CO2 savings data yet!',
                       ha='center', va='center', fontsize=12, color='gray',
                       transform=ax.transAxes)
        
        ax.set_title('Your CO2 Savings Over Time', fontsize=14, fontweight='bold', 
                    color=self.colors['primary'], pad=15)
        
        plt.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        return canvas
    
    def create_points_breakdown_chart(self, user_id: str, parent_frame) -> FigureCanvasTkAgg:
        """
        Create pie/bar chart showing points breakdown by category
        Returns: FigureCanvasTkAgg object to embed in Tkinter
        """
        df = self.get_user_transactions(user_id)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor('#f0f4f0')
        
        if df.empty or df[df['points'] > 0].empty:
            # No data - show placeholder
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, 'No points earned yet!\nStart earning green points.',
                       ha='center', va='center', fontsize=12, color='gray',
                       transform=ax.transAxes)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
        else:
            # Filter positive points only (not redemptions)
            points_df = df[df['points'] > 0].copy()
            
            # Group by activity type
            activity_points = points_df.groupby('activity_type')['points'].sum()
            
            # Colors for each category
            category_colors = [
                self.colors.get(cat, self.colors['accent']) 
                for cat in activity_points.index
            ]
            
            # Pie Chart
            ax1.set_facecolor('#ffffff')
            wedges, texts, autotexts = ax1.pie(
                activity_points.values, 
                labels=activity_points.index.str.title(),
                autopct='%1.1f%%',
                colors=category_colors,
                explode=[0.02] * len(activity_points),
                shadow=False,
                startangle=90
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax1.set_title('Points by Category', fontsize=12, fontweight='bold',
                         color=self.colors['primary'])
            
            # Bar Chart - breakdown by specific categories
            ax2.set_facecolor('#ffffff')
            category_points = points_df.groupby('category')['points'].sum().sort_values(ascending=True)
            
            bars = ax2.barh(range(len(category_points)), category_points.values,
                           color=self.colors['secondary'], edgecolor=self.colors['primary'])
            
            ax2.set_yticks(range(len(category_points)))
            ax2.set_yticklabels([c.replace('_', ' ').title() for c in category_points.index])
            ax2.set_xlabel('Points Earned', fontsize=11)
            ax2.set_title('Points by Activity', fontsize=12, fontweight='bold',
                         color=self.colors['primary'])
            
            # Add value labels on bars
            for i, (bar, val) in enumerate(zip(bars, category_points.values)):
                ax2.text(val + max(category_points.values) * 0.02, i, 
                        f'{int(val):,}', va='center', fontsize=9)
        
        plt.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        return canvas
    
    def create_summary_stats(self, user_id: str) -> dict:
        """Get summary statistics for user"""
        df = self.get_user_transactions(user_id)
        
        if df.empty:
            return {
                'total_points_earned': 0,
                'total_co2_saved': 0,
                'total_trips': 0,
                'total_recycling': 0,
                'total_drives': 0,
                'total_redeemed': 0
            }
        
        positive_points = df[df['points'] > 0]['points'].sum()
        redeemed_points = abs(df[df['points'] < 0]['points'].sum())
        
        return {
            'total_points_earned': int(positive_points),
            'total_co2_saved': float(df['co2_saved'].sum()),
            'total_trips': len(df[df['activity_type'] == 'transport']),
            'total_recycling': len(df[df['activity_type'] == 'recycling']),
            'total_drives': len(df[df['activity_type'] == 'drive']),
            'total_redeemed': int(redeemed_points)
        }
    
    def close_figures(self):
        """Close all matplotlib figures to free memory"""
        plt.close('all')
