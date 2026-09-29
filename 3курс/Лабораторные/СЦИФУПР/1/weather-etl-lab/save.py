import logging
import os
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from config import DB_URL
from models import WeatherPoint as WeatherPointModel

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class WeatherPoint(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(100), default="")
    date: Mapped[date] = mapped_column(Date, index=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    temp_min: Mapped[float] = mapped_column(Float, default=0.0)
    temp_max: Mapped[float] = mapped_column(Float, default=0.0)
    humidity: Mapped[float] = mapped_column(Float, default=0.0)
    windspeed: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


engine = create_engine(DB_URL, echo=False, future=True)


def init_db() -> None:
    if not os.path.exists("weather.db"):
        logger.info("Создание базы данных: %s", "weather.db")
    else:
        os.remove("weather.db")
    Base.metadata.create_all(engine)
    logger.info("База данных и таблицы созданы")


def save_points(points: list[WeatherPointModel], city: str = "") -> None:
    logger.info("Сохранение %d точек", len(points))

    with Session(engine) as session:
        existing_dates: set[date] = set(
            session.scalars(select(WeatherPoint.date)).all()
        )

        new_points = [p for p in points if p.date not in existing_dates]

        session.add_all(
            WeatherPoint(
                city=city,
                date=p.date,
                temperature=p.temperature,
                temp_min=p.temp_min,
                temp_max=p.temp_max,
                humidity=p.humidity,
                windspeed=p.windspeed,
                description=p.description,
            )
            for p in new_points
        )
        session.commit()
        logger.info("Сохранено %d новых записей", len(new_points))


def load_points() -> list[WeatherPoint]:
    with Session(engine) as session:
        logger.info("Загрузка точек из БД")
        query = select(WeatherPoint).order_by(WeatherPoint.date)
        return list(session.scalars(query).all())
