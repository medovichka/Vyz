from dataclasses import dataclass
from datetime import date


class geodata:
    status: str
    city: str
    lat: float
    lon: float


@dataclass
class WeatherPoint:
    date: date = None
    temperature: float = 0.0
    temp_min: float = 0.0
    temp_max: float = 0.0
    humidity: float = 0.0
    windspeed: float = 0.0
    description: str = ""

@dataclass
class WeatherReport:
    cod: int
    message: str
    cnt: int
    Points: tuple[WeatherPoint]