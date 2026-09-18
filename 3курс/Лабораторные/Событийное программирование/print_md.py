from DTO import WeatherPoint


def days_to_markdown(days: list[WeatherPoint]) -> str:
    lines = [
        "# Прогноз погоды",
        "",
        "| Дата | Сводка | Температура | Мин | Макс | Влажность | Ветер | ",
        "|------|------:|----:|-----:|-------:|------:|----------|",
    ]
    for d in days:
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
    return "\n".join(lines)
