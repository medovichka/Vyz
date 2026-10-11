"""ORM-модель события аудита.

Аудит — это не логи приложения, а бизнес-события с понятной семантикой,
привязанные к субъекту действия. Соглашение об именах событий:
``<объект>.<действие>`` в нижнем регистре через точку — например
``user.created``, ``user.login.success``, ``client.created``, ``user.disabled``.

В аудит НИКОГДА не попадают пароли, хэши, токены и прочие секреты — только
метаданные о факте события.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class AuditEvent(Base):
    """Запись о значимом действии пользователя или администратора."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Тип события вида "user.login.success". Индекс нужен для фильтрации в админке.
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    # Автор события. NULL — анонимное событие (например, неудачный логин
    # несуществующего пользователя или регистрация до создания записи).
    # ondelete="SET NULL": удаление пользователя не должно уносить историю аудита.
    #
    # Примечание: все nullable-колонки ниже аннотированы без `| None`/`Optional`.
    # SQLAlchemy 2.0.35 на Python 3.14 падает при разборе union-аннотаций
    # (`TypeError: descriptor '__getitem__' requires a 'typing.Union' object`),
    # а версии зависимостей зафиксированы заданием. Фактическая «nullable»
    # задаётся явно через `nullable=True`.
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Идентификатор OAuth-клиента, если событие пришло от приложения.
    # Это именно строка client_id, а не FK на oauth_clients: события аудита
    # должны читаться даже если клиент удалён.
    client_id: Mapped[str] = mapped_column(String(64), nullable=True)

    # Откуда пришло событие. 45 символов — максимальная длина IPv6 с портом/скобками.
    ip: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=True)

    # Произвольные данные о событии (например, {"email": "..."} при неудачном логине).
    # Имя metadata_json выбрано намеренно: атрибут `metadata` в декларативных моделях
    # SQLAlchemy занят объектом MetaData.
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        server_default=func.now(),
    )

    def __repr__(self) -> str:  # pragma: no cover - отладочный вывод
        return (
            f"<AuditEvent id={self.id} type={self.event_type!r} "
            f"actor_id={self.actor_id} client_id={self.client_id!r}>"
        )
