"""
Variable-validation tests for application configuration (app/config.py).

Covers the Settings class per the project test policy:
- default values for every configuration variable
- valid values and boundary values
- invalid values must raise clear, actionable errors
- production safety guards (CORS + JWT secret)
- the cached get_settings() accessor

These tests are pure unit tests: no database connection is made
(DATABASE_URL only needs to be present as a string for validation).
Environment variables are manipulated with pytest's monkeypatch so each
test is independent and deterministic.
"""

import pytest

from app.config import Settings, get_settings

DUMMY_DB = "postgresql://user:pass@localhost:5432/amap_test"
LONG_SECRET = "x" * 40  # >= 32 chars: passes the production length guard


def make_settings(monkeypatch, **env):
    """Construct Settings with a controlled environment.

    Starts from a clean slate (all AMAP-relevant variables removed), then
    applies the caller's overrides plus a default DATABASE_URL.
    """
    for var in (
        "ENVIRONMENT",
        "APP_NAME",
        "API_VERSION_PREFIX",
        "LOG_LEVEL",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "CORS_ALLOWED_ORIGINS",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(var, raising=False)
    env.setdefault("DATABASE_URL", DUMMY_DB)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return Settings()


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_default_development_environment(self, monkeypatch):
        s = make_settings(monkeypatch)
        assert s.environment == "development"
        assert s.is_production is False

    def test_default_app_metadata(self, monkeypatch):
        s = make_settings(monkeypatch)
        assert s.app_name == "AMAP Backend"
        assert s.api_version_prefix == "/api/v1"
        assert s.log_level == "INFO"

    def test_default_jwt_settings(self, monkeypatch):
        s = make_settings(monkeypatch)
        assert s.jwt_algorithm == "HS256"
        assert s.access_token_expire_minutes == 60
        # Development fallback secret (must never pass in production — tested below)
        assert s.jwt_secret_key == "amap-dev-jwt-secret-key-change-in-production-mode"

    def test_default_dev_cors_origins(self, monkeypatch):
        s = make_settings(monkeypatch)
        assert s.cors_allowed_origins == [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    def test_default_supabase_settings_are_empty(self, monkeypatch):
        s = make_settings(monkeypatch)
        assert s.supabase_url == ""
        assert s.supabase_anon_key == ""
        assert s.supabase_service_role_key == ""


# ---------------------------------------------------------------------------
# Valid values
# ---------------------------------------------------------------------------

class TestValidValues:
    def test_custom_values_are_honoured(self, monkeypatch):
        s = make_settings(
            monkeypatch,
            ENVIRONMENT="development",
            APP_NAME="AMAP CI",
            API_VERSION_PREFIX="/api/v2",
            LOG_LEVEL="DEBUG",
            JWT_ALGORITHM="HS512",
            ACCESS_TOKEN_EXPIRE_MINUTES="120",
        )
        assert s.app_name == "AMAP CI"
        assert s.api_version_prefix == "/api/v2"
        assert s.log_level == "DEBUG"
        assert s.jwt_algorithm == "HS512"
        assert s.access_token_expire_minutes == 120

    def test_cors_origins_parsed_and_trimmed(self, monkeypatch):
        s = make_settings(monkeypatch, CORS_ALLOWED_ORIGINS=" https://a.example , https://b.example ")
        assert s.cors_allowed_origins == ["https://a.example", "https://b.example"]

    def test_cors_empty_entries_are_dropped(self, monkeypatch):
        s = make_settings(monkeypatch, CORS_ALLOWED_ORIGINS="https://a.example,, ,https://b.example,")
        assert s.cors_allowed_origins == ["https://a.example", "https://b.example"]

    def test_explicit_cors_overrides_dev_default(self, monkeypatch):
        s = make_settings(monkeypatch, CORS_ALLOWED_ORIGINS="https://only.example")
        assert s.cors_allowed_origins == ["https://only.example"]

    def test_production_with_valid_config_passes(self, monkeypatch):
        s = make_settings(
            monkeypatch,
            ENVIRONMENT="production",
            CORS_ALLOWED_ORIGINS="https://app.example",
            JWT_SECRET_KEY=LONG_SECRET,
        )
        assert s.is_production is True
        assert s.cors_allowed_origins == ["https://app.example"]

    def test_non_dev_non_prod_environment_has_no_default_origins(self, monkeypatch):
        # Documented behaviour: only "development" gets localhost defaults;
        # any other environment must set CORS explicitly (production
        # enforces this at validation, staging does not).
        s = make_settings(monkeypatch, ENVIRONMENT="staging")
        assert s.environment == "staging"
        assert s.cors_allowed_origins == []


# ---------------------------------------------------------------------------
# Boundary values
# ---------------------------------------------------------------------------

class TestBoundaries:
    def test_minimum_length_production_secret_accepted(self, monkeypatch):
        s = make_settings(
            monkeypatch,
            ENVIRONMENT="production",
            CORS_ALLOWED_ORIGINS="https://app.example",
            JWT_SECRET_KEY="y" * 32,  # exactly at the boundary
        )
        assert len(s.jwt_secret_key) == 32

    def test_whitespace_padded_cors_entries_are_trimmed_to_valid(self, monkeypatch):
        s = make_settings(monkeypatch, CORS_ALLOWED_ORIGINS="   https://a.example   ")
        assert s.cors_allowed_origins == ["https://a.example"]


# ---------------------------------------------------------------------------
# Invalid values — clear errors
# ---------------------------------------------------------------------------

class TestInvalidValues:
    def test_missing_database_url_raises(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        with pytest.raises(RuntimeError, match="DATABASE_URL must be explicitly set"):
            Settings()

    def test_empty_database_url_raises(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "")
        with pytest.raises(RuntimeError, match="DATABASE_URL must be explicitly set"):
            Settings()

    def test_production_without_cors_raises(self, monkeypatch):
        with pytest.raises(RuntimeError, match="CORS_ALLOWED_ORIGINS must be explicitly set"):
            make_settings(monkeypatch, ENVIRONMENT="production")

    def test_production_with_empty_cors_raises(self, monkeypatch):
        with pytest.raises(RuntimeError, match="CORS_ALLOWED_ORIGINS must be explicitly set"):
            make_settings(monkeypatch, ENVIRONMENT="production", CORS_ALLOWED_ORIGINS=" , ")

    def test_production_with_default_jwt_secret_raises(self, monkeypatch):
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            make_settings(
                monkeypatch,
                ENVIRONMENT="production",
                CORS_ALLOWED_ORIGINS="https://app.example",
                # JWT_SECRET_KEY left unset -> dev default -> must be rejected
            )

    def test_production_with_short_jwt_secret_raises(self, monkeypatch):
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            make_settings(
                monkeypatch,
                ENVIRONMENT="production",
                CORS_ALLOWED_ORIGINS="https://app.example",
                JWT_SECRET_KEY="too-short",  # 9 chars < 32
            )

    def test_production_with_whitespace_jwt_secret_raises(self, monkeypatch):
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            make_settings(
                monkeypatch,
                ENVIRONMENT="production",
                CORS_ALLOWED_ORIGINS="https://app.example",
                JWT_SECRET_KEY=" " * 40,  # long enough but blank
            )

    def test_non_numeric_expire_minutes_raises_valueerror(self, monkeypatch):
        with pytest.raises(ValueError, match="invalid literal for int"):
            make_settings(monkeypatch, ACCESS_TOKEN_EXPIRE_MINUTES="sixty")

    def test_zero_expire_minutes_is_accepted(self, monkeypatch):
        # Documented current behaviour: no positivity guard exists on the
        # token lifetime. If this is ever deemed invalid, add the guard and
        # flip this test to pytest.raises.
        s = make_settings(monkeypatch, ACCESS_TOKEN_EXPIRE_MINUTES="0")
        assert s.access_token_expire_minutes == 0


# ---------------------------------------------------------------------------
# Cached accessor
# ---------------------------------------------------------------------------

class TestGetSettings:
    @pytest.fixture(autouse=True)
    def _clear_settings_cache(self):
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()  # never leak env-mutated settings into other tests

    def test_get_settings_is_cached(self):
        assert get_settings() is get_settings()

    def test_cache_clear_picks_up_new_environment(self, monkeypatch):
        first = get_settings()
        assert first.environment == "development" or True  # whatever the ambient env is
        get_settings.cache_clear()
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.example")
        monkeypatch.setenv("JWT_SECRET_KEY", LONG_SECRET)
        monkeypatch.setenv("DATABASE_URL", DUMMY_DB)
        second = get_settings()
        assert second is not first
        assert second.is_production is True
