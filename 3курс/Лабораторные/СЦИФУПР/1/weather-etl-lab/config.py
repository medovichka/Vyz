import os

from dotenv import load_dotenv

load_dotenv()


# OpenWeatherMap ---
WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL: str = os.getenv(
    "WEATHER_API_BASE_URL", "https://api.openweathermap.org/data/2.5"
)
# OpenWeatherMap ---

# IP ---
GEO_API_URL: str = os.getenv("GEO_API_URL")
GEO_API_FALLBACK_CITY: str = os.getenv("GEO_API_FALLBACK_CITY")
# IP ---

# DB ---
DB_URL: str = os.getenv("DB_URL")
# DB ---
