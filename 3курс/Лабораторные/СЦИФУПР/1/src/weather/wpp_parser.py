import logging
from datetime import datetime, timedelta
from typing import Any

from models import WeatherPoint

logger = logging.getLogger(__name__)


def parse_weather(raw_data: dict[str, Any]) -> list[WeatherPoint]:
    DAYS: list[WeatherPoint] = []
    list_of_points: list[dict[str, Any]] = raw_data["list"]

    today = datetime.now().date()  # noqa: DTZ005
    end_date = today + timedelta(days=3)

    for day in list_of_points:
        point_date = datetime.fromisoformat(day["dt_txt"]).date()
        if point_date < today or point_date > end_date:
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
        logger.debug("добавляем точку с датой %s", point_date)

    logger.info("Всего точек: %d", len(DAYS))
    logger.debug("Все точки:\n%s", DAYS)
    return DAYS
