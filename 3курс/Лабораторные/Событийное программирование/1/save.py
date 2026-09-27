from datetime import date

from sqlalchemy import Date, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from DTO import WeatherPoint as WeatherPointDTO


class Base(DeclarativeBase):
    pass


class WeatherPoint(Base):
    __tablename__ = "weather"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    temperature: Mapped[float]
    temp_min: Mapped[float]
    temp_max: Mapped[float]
    humidity: Mapped[int]
    windspeed: Mapped[float]
    description: Mapped[str] = mapped_column(String(100))


engine = create_engine("sqlite:///weather.db")
print("Создание таблиц")
Base.metadata.create_all(engine)


def save_points(points: list[WeatherPointDTO]) -> None:
    print("сохранение точек")
    with Session(engine) as session:
        session.add_all(
            WeatherPoint(
                date=p.date,
                temperature=p.temperature,
                temp_min=p.temp_min,
                temp_max=p.temp_max,
                humidity=p.humidity,
                windspeed=p.windspeed,
                description=p.description,
            )
            for p in points
        )

        session.commit()

def load_points() -> list[WeatherPoint]:
    with Session(engine) as session:
        session.get()