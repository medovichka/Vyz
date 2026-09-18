import os

from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

MY_IP = os.getenv("MY_IP")

API_KEY = os.getenv("WEATHER_API_KEY")
