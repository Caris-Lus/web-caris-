"""
Transport module for Green Points Application
Handles route selection and CO2 calculation
"""

import os
import pandas as pd

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import POINTS_CONFIG, CO2_EMISSIONS, TRANSACTIONS_FILE
from modules.utils import (
    calculate_distance, get_location_coordinates, find_closest_location,
    generate_id, get_timestamp, get_locations_list
)


class TransportManager:
    """Manages transport-related calculations and points"""
    
    def __init__(self):
        self.transport_modes = {
            'walking': {
                'name': 'Walking',
                'icon': 'Walk',
                'points_per_km': POINTS_CONFIG['transport']['walking'],
                'co2_per_km': CO2_EMISSIONS['walking'],
                'description': 'Healthiest option - Zero emissions!'
            },
            'cycling': {
                'name': 'Cycling',
                'icon': 'Cycle',
                'points_per_km': POINTS_CONFIG['transport']['cycling'],
                'co2_per_km': CO2_EMISSIONS['cycling'],
                'description': 'Fast & eco-friendly!'
            },
            'public_transport': {
                'name': 'Public Transport',
                'icon': 'Bus/Train',
                'points_per_km': POINTS_CONFIG['transport']['public_transport'],
                'co2_per_km': CO2_EMISSIONS['public_transport'],
                'description': 'Shared transport - Lower emissions!'
            }
        }
    
    def get_available_locations(self) -> list:
        """Get list of available locations"""
        return get_locations_list()
    
    def validate_location(self, location: str) -> tuple:
        """
        Validate and find matching location
        Returns: (is_valid, matched_location or error_message)
        """
        if not location or len(location.strip()) < 2:
            return (False, "Please enter a valid location")
        
        matched = find_closest_location(location.strip())
        if matched:
            return (True, matched)
        
        return (False, f"Location '{location}' not found. Try: {', '.join(get_locations_list()[:5])}...")
    
    def calculate_route(self, source: str, destination: str) -> dict:
        """
        Calculate route details between two locations
        Returns: {'success': bool, 'data': dict or 'message': str}
        """
        # Validate source
        source_valid, source_result = self.validate_location(source)
        if not source_valid:
            return {'success': False, 'message': f"Source: {source_result}"}
        
        # Validate destination
        dest_valid, dest_result = self.validate_location(destination)
        if not dest_valid:
            return {'success': False, 'message': f"Destination: {dest_result}"}
        
        # Check if same location
        if source_result.lower() == dest_result.lower():
            return {'success': False, 'message': "Source and destination cannot be the same"}
        
        # Get coordinates
        source_coords = get_location_coordinates(source_result)
        dest_coords = get_location_coordinates(dest_result)
        
        if not source_coords or not dest_coords:
            return {'success': False, 'message': "Could not find coordinates"}
        
        # Calculate distance
        distance = calculate_distance(
            source_coords[0], source_coords[1],
            dest_coords[0], dest_coords[1]
        )
        
        # Calculate options for each transport mode
        options = []
        car_co2 = distance * CO2_EMISSIONS['car']
        
        for mode_key, mode_info in self.transport_modes.items():
            mode_co2 = distance * mode_info['co2_per_km']
            co2_saved = car_co2 - mode_co2
            points = int(distance * mode_info['points_per_km'])
            
            # Estimate time (rough estimates)
            if mode_key == 'walking':
                time_mins = int(distance * 12)  # ~5 km/h
            elif mode_key == 'cycling':
                time_mins = int(distance * 4)   # ~15 km/h
            else:
                time_mins = int(distance * 3)   # ~20 km/h with stops
            
            options.append({
                'mode': mode_key,
                'name': mode_info['name'],
                'description': mode_info['description'],
                'distance_km': distance,
                'time_mins': time_mins,
                'co2_emission': mode_co2,
                'co2_saved': co2_saved,
                'points': points
            })
        
        return {
            'success': True,
            'data': {
                'source': source_result,
                'destination': dest_result,
                'distance_km': distance,
                'car_co2_baseline': car_co2,
                'options': options
            }
        }
    
    def record_trip(self, user_id: str, mode: str, distance: float, 
                    source: str, destination: str) -> dict:
        """
        Record a completed trip and award points
        Returns: {'success': bool, 'points': int, 'co2_saved': float}
        """
        if mode not in self.transport_modes:
            return {'success': False, 'message': 'Invalid transport mode'}
        
        mode_info = self.transport_modes[mode]
        car_co2 = distance * CO2_EMISSIONS['car']
        mode_co2 = distance * mode_info['co2_per_km']
        co2_saved = car_co2 - mode_co2
        points = int(distance * mode_info['points_per_km'])
        
        # Create transaction record
        transaction = {
            'transaction_id': generate_id(),
            'user_id': user_id,
            'activity_type': 'transport',
            'category': mode,
            'points': points,
            'co2_saved': co2_saved,
            'details': f"{source} to {destination} ({distance:.2f} km)",
            'timestamp': get_timestamp(),
            'status': 'completed'
        }
        
        # Save to CSV
        pd.DataFrame([transaction]).to_csv(TRANSACTIONS_FILE, mode='a', header=False, index=False)
        
        return {
            'success': True,
            'points': points,
            'co2_saved': co2_saved,
            'message': f"Trip recorded! Earned {points} points and saved {co2_saved:.0f}g CO2"
        }
