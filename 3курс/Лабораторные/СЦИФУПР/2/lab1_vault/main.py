import pytest
from pydantic import ValidationError

from app.config import Settings, SettingsConfigDict


def test_missing_required_field(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    class TestSettings(Settings):
        model_config = SettingsConfigDict(env_file=None)

    with pytest.raises(ValidationError) as exc_info:
        TestSettings()

    missing = {e["loc"][0] for e in exc_info.value.errors() if e["type"] == "missing"}
    assert {"database_url", "secret_key"} <= missing
