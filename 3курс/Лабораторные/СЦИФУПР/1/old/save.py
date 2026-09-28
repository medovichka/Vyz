import sqlite3
from old.parsepoints import parse_weather, WeatherPoint
def save_days(days: list[WeatherPoint], db_path: str = "data.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                date        TEXT,
                temperature REAL,
                temp_min    REAL,
                temp_max    REAL,
                humidity    REAL,
                windspeed   REAL,
                description TEXT
            )
        """)

        conn.executemany("""
            INSERT OR REPLACE INTO weather
            (date, temperature, temp_min, temp_max, humidity, windspeed, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (
                d.date.isoformat(),
                d.temperature,
                d.temp_min,
                d.temp_max,
                d.humidity,
                d.windspeed,
                d.description,
            )
            for d in days
        ])

def days_to_markdown(days) -> str:
    lines = [
        "# Прогноз погоды",
        "",
        "| Дата | Темп. | Мин | Макс | Влажн. | Ветер | Описание |",
        "|------|------:|----:|-----:|-------:|------:|----------|",
    ]
    for d in days:
        date_str = d.date.isoformat() if hasattr(d.date, "isoformat") else d.date
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



if __name__ == "__main__":
    days = parse_weather()
    save_days(days)
    print(f"Сохранено {len(days)} записей")

    md = days_to_markdown(days)
    print(md)

    with open("weather.md", "w", encoding="utf-8") as f:
        f.write(md)