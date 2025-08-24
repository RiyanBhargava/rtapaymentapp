# RTA Payment Scanner Configuration
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ByteDance API Configuration
BYTEPLUS_API_KEY = os.getenv("BYTEPLUS_API_KEY")  # Get from environment variable
BYTEPLUS_BASE_URL = os.getenv("BYTEPLUS_BASE_URL", "https://ark.ap-southeast-1.bytepluses.com/api/v3")
BYTEPLUS_MODEL = os.getenv("BYTEPLUS_MODEL", "seed-1-6-250615")

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# RTA Fare Configuration (in AED)
TAXI_BASE_FARE = 12.0
TAXI_PER_KM = 8.0
METRO_BASE_FARE = 3.0
METRO_PER_KM = 0.5
BUS_BASE_FARE = 2.0
BUS_PER_KM = 0.3

# Dubai Transport Stops
DUBAI_STOPS = [
    "Dubai Marina Walk",
    "Mall of the Emirates Metro Station", 
    "Union Metro Station",
    "Union Bus Terminal",
    "Gold Souq Bus Station",
    "Ras Al Khor Industrial Area",
    "Dubai Mall",
    "Burj Khalifa",
    "Dubai Airport",
    "DIFC",
    "Downtown Dubai",
    "JBR",
    "Business Bay",
    "Dubai Marina",
    "Ibn Battuta Mall",
    "MOE",
    "Deira City Centre",
    "Dubai Festival City",
    "Al Ghubaiba Bus Station",
    "Bur Dubai Abra Station",
    "Karama",
    "Satwa",
    "Al Fahidi Metro Station",
    "Creek Metro Station",
    "Salah Al Din Metro Station"
]
