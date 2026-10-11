"""Конфигурация приложения: все настройки и секреты читаются из окружения/``.env``.

Прямого ``os.getenv`` в коде нет: ``pydantic-settings`` сам читает переменные
окружения и файл ``.env``, приводит типы и валидирует значения. Если обязательное
поле не задано (или не проходит валидацию), приложение падает на старте с
понятной ошибкой ``ValidationError``, а не в рантайме где-то в глубине запроса.

Шаблон для заполнения — ``.env.example``. Реальный ``.env`` в репозиторий
не попадает (см. ``.gitignore``).
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки Vault.

    Регистр имён переменных не важен: ``pydantic-settings`` по умолчанию
    сравнивает их без учёта регистра, поэтому ``JWT_SECRET`` и ``jwt_secret``
    в ``.env`` равнозначны.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Инфраструктура ---
    app_name: str = "Vault"
    environment: str = "development"
    debug: bool = False
    database_url: str

    # --- JWT (HS256 на этом этапе) ---
    jwt_secret: str = Field(..., min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_ttl_min: int = Field(default=60, gt=0)

    # --- Пароли (Argon2id + pepper) ---
    password_pepper: str = Field(..., min_length=16)
    password_min_length: int = Field(default=12, ge=8)


settings = Settings()
