from models import WeatherPoint


def points_to_markdown(points: list[WeatherPoint]):
    lines = [
        "# Прогноз погоды",
        "",
        "| Дата | Сводка | Температура | Мин | Макс | Влажность | Ветер | ",
        "|------|------:|----:|-----:|-------:|------:|----------|",
    ]
    print("Сохраняем точки в md")
    for d in points:
        date_str = d.date.isoformat()
        lines.append(
            f"| {date_str} "
            f"| {d.temperature:.1f}°C "
            f"| {d.temp_min:.1f}°C "
            f"| {d.temp_max:.1f}°C "
            f"| {d.humidity:.0f}% "
            f"| {d.windspeed:.1f} м/с "
            f"| {d.description} |"
        )
        with open("weather.md", "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
    print("Сохранено")
