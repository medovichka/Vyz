import logging

from api_caller import get_data, get_geo, get_weather_points
from config import GEO_API_FALLBACK_CITY, WEATHER_API_KEY
from save import init_db, load_points, save_points
from to_md import points_to_markdown
from wpp_parser import parse_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    if not WEATHER_API_KEY:
        logger.error("WEATHER_API_KEY не задан")
        return
    # координаты
    try:
        init_db()
        ip_json = get_data("https://ipinfo.io/json")
        ip = ip_json.get("ip")
        lat, lon = get_geo(ip)
    except Exception:
        logger.exception("Не удалось определить координаты")
        return

    # прогноз
    try:
        raw_weather = get_weather_points(lat=lat, lon=lon)
    except Exception:
        logger.exception("Не удалось получить прогноз погоды")
        return

    # парсинг
    parsed_points = parse_weather(raw_weather)
    if not parsed_points:
        logger.warning("Нет данных для сохранения.")
        return

    # сохранение
    try:
        save_points(parsed_points, city=GEO_API_FALLBACK_CITY or "auto")
    except Exception:
        logger.exception("Ошибка при сохранении в БД")
        return

    # вывод в Markdown
    try:
        points = load_points()
        points_to_markdown(points, city=GEO_API_FALLBACK_CITY or "auto")
    except Exception:
        logger.exception("Ошибка при выгрузке в Markdown")
        return


if __name__ == "__main__":
    main()
