"""Базовый декларативный класс для всех ORM-моделей Vault.

В SQLAlchemy 2.x вместо устаревшей фабрики ``declarative_base()`` используется
класс-наследник ``DeclarativeBase``. Все модели приложения наследуются от
``Base``, а Alembic в ``alembic/env.py`` берёт ``Base.metadata`` в качестве
``target_metadata`` для автогенерации миграций.
"""

from datetime import datetime, timezone

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Единое соглашение об именовании ограничений (constraints).
# Нужно, чтобы SQLite/PostgreSQL создавали предсказуемые имена индексов,
# внешних ключей и UNIQUE-ограничений: без этого Alembic не сможет
# корректно генерировать операции их удаления/изменения в будущих миграциях.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Общий предок всех декларативных моделей приложения.

    Дочерние модели описываются в аннотированном стиле SQLAlchemy 2.x::

        class User(Base):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(primary_key=True)
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def utcnow() -> datetime:
    """Текущее время в UTC (timezone-aware).

    Общий помощник для значений по умолчанию у колонок ``created_at``:
    одна реализация на все модели, чтобы время создания записи считалось
    в одной и той же зоне.
    """
    return datetime.now(timezone.utc)
