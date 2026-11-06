import logging

from models import WeatherPoint

logger = logging.getLogger(__name__)


def points_to_markdown(
    points: list[WeatherPoint],
    city: str = "",
) -> None:
    if not points:
        logger.warning("Нет данных для вывода")
        return

    dates = sorted(p.date for p in points if p.date)
    output_file: str = "weather_report.md"
    if dates:
        period = f"{dates[0].isoformat()} – {dates[-1].isoformat()}"
    else:
        period = "—"

    lines: list[str] = [
        "# Прогноз погоды",
        "",
        f"Автоматически определённая локация: {city or 'не определена'}  ",
        f"Период: {period}  ",
        "",
        "| Дата | Мин. темп. | Макс. темп. | Описание | Влажность | Ветер |",
        "|------|-----------------|------------------|----------|---------------|-------------|",
    ]

    for d in points:
        date_str = d.date.isoformat() if d.date else "—"
        lines.append(
            f"| {date_str} "
            f"| {d.temp_min:.1f} "
            f"| {d.temp_max:.1f} "
            f"| {d.description} "
            f"| {d.humidity:.0f} "
            f"| {d.windspeed:.1f} |"
        )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Markdown сохранён в %s", output_file)
