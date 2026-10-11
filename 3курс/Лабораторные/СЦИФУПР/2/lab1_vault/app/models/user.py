"""ORM-модель пользователя Vault."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class User(Base):
    """Пользователь сервиса.

    Пароль в открытом виде не хранится никогда — только Argon2id-хэш
    (см. ``app/core/passwords.py``). Поле ``is_admin`` управляет доступом
    к админским полям GraphQL-схемы.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # unique + index: на email опирается и логин, и проверка «email уже занят».
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # default — значение подставляет ORM (работает на любом диалекте),
    # server_default — значение по умолчанию на стороне БД для «сырых» INSERT'ов.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    def __repr__(self) -> str:  # pragma: no cover - отладочный вывод
        return (
            f"<User id={self.id} email={self.email!r} "
            f"is_active={self.is_active} is_admin={self.is_admin}>"
        )
