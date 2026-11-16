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

    @classmethod
    def from_env(
        cls, env: Mapping[str, str] = os.environ, config_path: str = CONFIG_PATH
    ) -> "Settings":
        """
        Read SAM_API_KEY and MS_URL from the environment and load config.yaml
        """
        return cls(
            sam_api_key=env["SAM_API_KEY"],
            ms_webhook_url=env["MS_URL"],
            config=load_config(config_path),
        )
