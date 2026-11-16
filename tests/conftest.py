"""
Shared test fixtures
"""

import pytest

import client


@pytest.fixture
def api_client():
    api_config = client.Configuration()
    api_config.access_token = "abcd"
    api_config.host = "https://www.example.com"

    return client.ApiClient(api_config)


@pytest.fixture
def config():
    return {
        "sam_url": "https://api.sam.gov/opportunities/v2/search",
        "from_days_back": 1,
        "naics": [{"code": 541511}],
        "agencies": [
            {"agency": "ENERGY, DEPARTMENT OF", "abbr": "Energy"},
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }


def make_record(n: int) -> dict:
    return {
        "title": f"Test title {n}",
        "agency": "ENERGY, DEPARTMENT OF.ENERGY, DEPARTMENT OF.NNSA NON-MO CNTRCTNG OPS DIV",
        "posted_date": "2024-02-25",
        "type": "Special Notice",
        "set_aside": "SBA",
        "due_date": "2024-03-12T23:59:00-04:00",
        "naics": "541511",
        "url": f"https://sam.gov/opp/{n}/view",
    }
