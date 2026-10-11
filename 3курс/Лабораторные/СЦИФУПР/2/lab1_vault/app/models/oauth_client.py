"""ORM-модель OAuth-клиента.

На этом этапе хранятся только метаданные приложения-клиента. Секреты клиента
(``client_secret``), разрешённые grant-типы и refresh-токены появятся во второй
лабораторной вместе с полноценным OAuth2/OIDC.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class OAuthClient(Base):
    """Зарегистрированное приложение, которое ходит в Vault."""

    __tablename__ = "oauth_clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Публичный идентификатор клиента (генерируется через uuid4 в мутации createClient).
    client_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Конфиденциальный клиент (server-side, умеет хранить секрет) либо публичный (SPA/мобильное).
    is_confidential: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Список разрешённых redirect URI. Хранится в JSON-колонке: для SQLite это TEXT,
    # для PostgreSQL — json/jsonb, код при этом не меняется.
    #
    # Важно: SQLAlchemy не отслеживает мутацию JSON «на месте» — `client.redirect_uris.append(...)`
    # не попадёт в UPDATE. Список нужно переприсваивать целиком:
    #     client.redirect_uris = [*client.redirect_uris, new_uri]
    redirect_uris: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    def __repr__(self) -> str:  # pragma: no cover - отладочный вывод
        return (
            f"<OAuthClient id={self.id} client_id={self.client_id!r} "
            f"name={self.name!r} is_confidential={self.is_confidential}>"
        )
