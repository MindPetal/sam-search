"""
Load run settings: secrets from the environment and search options from
config.yaml.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

import yaml

CONFIG_PATH = "config.yaml"


def load_config(path: str = CONFIG_PATH) -> dict:
    # Load yaml config file
    with open(path, "r") as file:
        return yaml.load(file, Loader=yaml.FullLoader)


@dataclass(frozen=True)
class Settings:
    sam_api_key: str
    ms_webhook_url: str
    config: dict
    slack_webhook_url: str = ""

    @classmethod
    def from_env(
        cls, env: Mapping[str, str] = os.environ, config_path: str = CONFIG_PATH
    ) -> "Settings":
        """
        Read SAM_API_KEY and at least one of MS_URL / SLACK_URL from the
        environment, and load config.yaml
        """
        ms_webhook_url, slack_webhook_url = read_webhook_urls(env)

        return cls(
            sam_api_key=env["SAM_API_KEY"],
            ms_webhook_url=ms_webhook_url,
            config=load_config(config_path),
            slack_webhook_url=slack_webhook_url,
        )


def read_webhook_urls(env: Mapping[str, str]) -> tuple[str, str]:
    """
    Read the MS Teams and Slack webhook URLs. Either may be blank, but not both.
    """
    ms_webhook_url = env.get("MS_URL", "").strip()
    slack_webhook_url = env.get("SLACK_URL", "").strip()

    if not ms_webhook_url and not slack_webhook_url:
        raise ValueError("Set MS_URL, SLACK_URL, or both")

    return ms_webhook_url, slack_webhook_url
