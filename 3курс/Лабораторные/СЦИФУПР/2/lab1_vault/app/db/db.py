"""Подключение к базе данных: движок SQLAlchemy, фабрика сессий, FastAPI-зависимость.

Модуль намеренно НЕ вызывает ``Base.metadata.create_all()``: схема управляется
миграциями Alembic (``alembic upgrade head``). ``create_all`` используется только
в тестах — там он уместен, потому что тестовая БД живёт в памяти и умирает вместе
с процессом.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


def build_engine(database_url: str | None = None) -> Engine:
    """Создать движок SQLAlchemy.

    :param database_url: строка подключения; по умолчанию берётся ``settings.database_url``.
        Отдельный параметр нужен тестам, чтобы поднимать изолированную БД в памяти.

    SQLite требует особой настройки:
      * ``check_same_thread=False`` — FastAPI исполняет синхронные зависимости
        в threadpool, а sqlite3 по умолчанию запрещает передавать соединение
        между потоками;
      * ``StaticPool`` для ``:memory:`` — база в памяти существует ровно столько,
        сколько живёт соединение, поэтому пул должен переиспользовать одно и то же
        соединение, иначе каждый коннект получит пустую БД.
    """
    url = database_url or settings.database_url

    kwargs: dict[str, object] = {
        "echo": settings.debug,
        # Проверять "живость" соединения перед выдачей из пула: защищает от
        # разорванных соединений (актуально для PostgreSQL).
        "pool_pre_ping": True,
    }

    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool

    return create_engine(url, **kwargs)


# Единственный движок на процесс: создаётся один раз при импорте модуля.
engine: Engine = build_engine()

# Фабрика сессий. Параметры:
#   autoflush=False     — не сбрасывать объекты в БД перед каждым запросом неявно;
#   expire_on_commit=False — после commit() объекты остаются «живыми»: их поля
#       доступны без повторного SELECT. Для GraphQL-резолверов это критично,
#       иначе обращение к полю после коммита в закрытой сессии даст
#       DetachedInstanceError.
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI-зависимость: выдаёт сессию и гарантированно закрывает её.

    Используется так::

        @router.get("/auth/me")
        def me(db: Session = Depends(get_db)) -> ...:
            ...

    Сессия закрывается в ``finally``, поэтому утечка соединений невозможна
    даже при исключении внутри обработчика.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
