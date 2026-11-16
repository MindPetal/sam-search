"""
Tests for config.py
"""

import pytest

from sam_search import config
from sam_search.config import Settings


def test_load_config(mocker):
    mocker.patch("builtins.open", mocker.mock_open(read_data="foo"))
    assert "foo" == config.load_config()


def test_settings_from_env(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("from_days_back: 1\nnaics:\n  - code: 541511\n")

    settings = Settings.from_env(
        {"SAM_API_KEY": "key", "MS_URL": "https://webhook.example.com"},
        config_path=str(config_path),
    )

    assert settings == Settings(
        sam_api_key="key",
        ms_webhook_url="https://webhook.example.com",
        config={"from_days_back": 1, "naics": [{"code": 541511}]},
    )


def test_settings_from_env_requires_secrets(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("from_days_back: 1\n")

    with pytest.raises(KeyError):
        Settings.from_env({"SAM_API_KEY": "key"}, config_path=str(config_path))


def test_repo_config_loads():
    # The checked-in config.yaml has every key the search needs
    loaded = config.load_config()

    assert {"sam_url", "from_days_back", "naics", "set_asides", "agencies"} <= set(
        loaded
    )
