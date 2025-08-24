# Sample Journey Data for Testing

SAMPLE_JOURNEY_1 = """
=== Detailed Journey with Lines/Bus Numbers ===
1. taxi: 1 stop, 8.5 min, 4.2 km
   Stops: Dubai Marina Walk -> Mall of the Emirates Metro Station

2. transfer (walk): 2 stops, 1.0 min, 0.02 km
   Stops: Mall of the Emirates Metro Station entrance -> Mall of the Emirates Metro Station 1

3. MRed1 (metro): 7 stops, 12.1 min, 15.8 km
   Stops: Mall of the Emirates Metro Station 1 -> Union Metro Station 2

4. transfer (walk): 3 stops, 2.0 min, 0.05 km
   Stops: Union Metro Station 2 -> Union Metro Station (Green Line) -> Union Bus Terminal

5. 64 (bus): 8 stops, 18.3 min, 12.4 km
   Stops: Union Bus Terminal -> Gold Souq Bus Station -> Ras Al Khor Industrial Area

6. transfer (walk): 2 stops, 1.5 min, 0.08 km
   Stops: Ras Al Khor Bus Stop -> Final Destination Office Building
"""

SAMPLE_JOURNEY_2 = """
1. taxi: 2 stops, 15.2 min, 8.7 km
   Stops: Dubai Airport -> Dubai Mall Metro Station

2. MRed1 (metro): 5 stops, 9.8 min, 12.3 km
   Stops: Dubai Mall Metro Station -> Burj Khalifa Metro Station

3. transfer (walk): 1 stop, 0.5 min, 0.01 km
   Stops: Burj Khalifa Metro Station -> Downtown Dubai
"""

SAMPLE_JOURNEY_3 = """
1. 11 (bus): 12 stops, 25.4 min, 18.6 km
   Stops: Ibn Battuta Mall -> MOE Bus Station

2. transfer (walk): 1 stop, 2.0 min, 0.03 km
   Stops: MOE Bus Station -> Mall of the Emirates Metro Station

3. MRed1 (metro): 8 stops, 14.2 min, 19.8 km
   Stops: Mall of the Emirates Metro Station -> DIFC Metro Station

4. taxi: 1 stop, 5.5 min, 2.8 km
   Stops: DIFC Metro Station -> Business Bay Office Tower
"""

def print_sample_journeys():
    """Print all sample journeys for easy copying"""
    print("=== SAMPLE JOURNEY 1 (Multi-Modal) ===")
    print(SAMPLE_JOURNEY_1)
    print("\n=== SAMPLE JOURNEY 2 (Simple) ===")
    print(SAMPLE_JOURNEY_2)
    print("\n=== SAMPLE JOURNEY 3 (Complex) ===")
    print(SAMPLE_JOURNEY_3)

if __name__ == "__main__":
    print_sample_journeys()
