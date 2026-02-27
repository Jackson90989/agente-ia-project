import pytest

from config import Config


@pytest.mark.unit
def test_config_defaults_present():
    assert Config.SECRET_KEY
    assert Config.JWT_SECRET_KEY
    assert Config.SQLALCHEMY_DATABASE_URI


@pytest.mark.unit
def test_database_uri_has_scheme():
    assert "://" in Config.SQLALCHEMY_DATABASE_URI
