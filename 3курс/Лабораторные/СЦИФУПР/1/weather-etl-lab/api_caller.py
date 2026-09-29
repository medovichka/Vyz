import logging
from typing import Any

import requests

from config import (
    GEO_API_URL,
    WEATHER_API_BASE_URL,
    WEATHER_API_KEY,
)

logger = logging.getLogger(__name__)


def get_data(API_URL: str, parametrs: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        response = requests.get(url=API_URL, params=parametrs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Таймаут при запросе к %s", API_URL)
        raise
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка соединения с %s", API_URL)
        raise
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code
        if status == 401:
            logger.error("Неверный API-ключ.")
        elif status == 404:
            logger.error("Ресурс не найден.")
        elif status == 429:
            logger.error("Превышен лимит запросов.")
        else:
            logger.error("Ошибка %s: %s", status, exc)
        raise
    except requests.exceptions.RequestException as exc:
        logger.error("Неизвестная ошибка запроса: %s", exc)
        raise


def get_geo(IP: str) -> tuple[float, float]:
    logger.info("Определение координат через %s", GEO_API_URL)

    info: dict[str, Any] = get_data(GEO_API_URL)
    loc: str | None = info.get("loc")
    if not loc:
        raise KeyError("Неправильный ответ от API")
    lat_str, lon_str = loc.split(",")
    lat, lon = float(lat_str), float(lon_str)
    city: str = info.get("city", "неизвестно")
    logger.info("Определён город: %s (lat=%.4f, lon=%.4f)", city, lat, lon)
    return lat, lon


def get_weather_points(lat: float, lon: float) -> dict[str, Any]:
    logger.info("Запрос прогноза погоды для lat=%.4f, lon=%.4f", lat, lon)

    url = f"{WEATHER_API_BASE_URL}/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    data: dict[str, Any] = get_data(url, parametrs=params)
    logger.info("Получено %d точек прогноза", data.get("cnt", 0))
    return data
