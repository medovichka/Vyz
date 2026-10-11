"""ORM-модели приложения.

Все модели импортируются здесь. Это важно: декларативный реестр SQLAlchemy
наполняется в момент импорта класса, поэтому к моменту чтения ``Base.metadata``
(в ``alembic/env.py`` или в тестах) достаточно сделать ``import app.models`` —
и все таблицы уже зарегистрированы, включая те, на которые ссылаются внешние ключи.
"""

from app.db.base import Base
from app.models.audit_event import AuditEvent
from app.models.oauth_client import OAuthClient
from app.models.user import User

__all__ = ["Base", "AuditEvent", "OAuthClient", "User"]
