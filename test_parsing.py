#!/usr/bin/env python3
"""Test journey parsing functionality"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import parse_journey_text, calculate_fare, parse_journey_manually, load_sample_journey

def test_parsing():
    print("=== TESTING JOURNEY PARSING ===\n")
    
    # Load sample journey
    sample_journey = load_sample_journey()
    journey_text = sample_journey['journey_text']
    
    print("Journey Text:")
    print(journey_text)
    print("\n" + "="*50 + "\n")
    
    # Test manual parsing
    result = parse_journey_manually(journey_text)
    
    print("Parsed Journey Steps:")
    for i, step in enumerate(result['journey_steps'], 1):
        print(f"{i}. {step['mode'].upper()}")
        print(f"   Line: {step.get('line_number', 'N/A')}")
        print(f"   Distance: {step['distance_km']} km")
        print(f"   Fare: {step['fare_aed']} AED")
        print(f"   Stops: {' -> '.join(step['stops']) if step['stops'] else 'N/A'}")
        print()
    
    print(f"Total Fare: {result['total_fare']} AED")
    print(f"Total Distance: {result['total_distance']} km")

if __name__ == "__main__":
    test_parsing()
