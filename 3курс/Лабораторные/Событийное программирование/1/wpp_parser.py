from datetime import datetime, timedelta

from DTO import WeatherPoint


def parse_weather(list_of_points: tuple[WeatherPoint]) -> tuple[WeatherPoint]:

    DAYS = []
    list_of_points = list_of_points["list"]
    today = datetime.now().date()  # noqa: DTZ005
    tomorrow = today + timedelta(days=1)
    zavtrazavtra = tomorrow + timedelta(days=1)

    for day in list_of_points:
        point_date = datetime.fromisoformat(day["dt_txt"]).date()
        if point_date > zavtrazavtra:
            continue
        DAYS.append(
            WeatherPoint(
                date=point_date,
                temperature=day["main"]["temp"],
                temp_min=day["main"]["temp_min"],
                temp_max=day["main"]["temp_max"],
                humidity=day["main"]["humidity"],
                windspeed=day["wind"]["speed"],
                description=day["weather"][0]["description"],
            )
        )
        print(f"добавляем точку с датой {point_date}")
    print(f"Все точки:\n{DAYS}")
    return DAYS


if __name__ == "__main__":
    print(parse_weather())
