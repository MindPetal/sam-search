"""
Entry point: read settings and run the search.
"""

import logging

from sam_search import search
from sam_search.config import Settings


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    search.main(Settings.from_env())


if __name__ == "__main__":
    run()
