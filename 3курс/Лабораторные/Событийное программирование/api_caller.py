import requests

from DTO import WeatherReport


def get_data(API_URL: str) -> str:
    response = requests.get(f"{API_URL}")
    print(f"запрос к {API_URL}")
    return response.json()


def get_geo(IP: str) -> tuple[float] | None:
    print(f"получение координат по IP = {IP}")
    info = get_data(f"http://ip-api.com/json/{IP}?fields=16592")
    print(f"получили: {info}")
    return info["lat"], info["lon"]


def get_weather_points(lat: float, lon: float, API: str) -> WeatherReport | None:
    print(f"получение прогноза погода по координатам {lat,lon}")
    weather_points = get_data(
        API_URL=f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API}&units=metric&lang=ru"
    )
    print(f"получили {weather_points["cnt"]} точек")
    return weather_points


#
# if __name__ == "__main__":
# print(get_geo())
# print(get_weather_points())
#
