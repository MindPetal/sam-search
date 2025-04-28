"""
    Tests for search.py 
"""

from datetime import date

import pytest

import client
import search


@pytest.fixture
def api_client():
    api_config = search.client.Configuration()
    api_config.access_token = "abcd"
    api_config.host = "https://www.example.com"

    return client.ApiClient(api_config)


def test_load_config(mocker):
    mocker.patch("builtins.open", mocker.mock_open(read_data="foo"))
    assert "foo" == search.load_config()


def test_search(mocker):
    api_response = client.ODataValueOfIEnumerableOfOppDto()
    opp_dto = client.OppDto()
    opp_dto.title = "Title"
    opp_dto.agency = "Agency name"
    opp_dto.posted_date = "01/01/1999"
    opp_dto.type = "Solicitation"
    opp_dto.set_aside = "SBA"
    opp_dto.due_date = "02/01/1999"
    opp_dto.naics = "541519"
    opp_dto.url = "https://example.com"
    api_response.value = [opp_dto]

    mocker.patch("search.client.SamApi.search", return_value=api_response)
    assert api_response.to_dict()["value"] == search.search(
        api_client, "abcd", "01/01/1999", "01/02/1999", 1000, "541519"
    )


def test_format_agency_two_str_match():
    agency = "AGENCY1.AGENCY2"
    agencies = [{"agency": "AGENCY2", "abbr": "ABBR"}]

    assert "ABBR" == search.format_agency(agency, agencies)


def test_format_agency_one_str_match():
    agency = "AGENCY1"
    agencies = [{"agency": "AGENCY1", "abbr": "ABBR"}]

    assert "ABBR" == search.format_agency(agency, agencies)


def test_format_agency_two_str_no_match():
    agency = "AGENCY1.AGENCY2"
    agencies = [{"agency": "FOO", "abbr": "ABBR"}]

    assert "AGENCY2" == search.format_agency(agency, agencies)


def test_format_agency_departmental_match():
    agency = "AGENCY1.DEPARTMENTAL OFFICES"
    agencies = [{"agency": "AGENCY1", "abbr": "ABBR"}]

    assert "ABBR" == search.format_agency(agency, agencies)


def test_format_date_posted_date():
    posted_date = "2024-02-25"

    assert "02/25/2024" == search.format_date(posted_date)


def test_format_date_due_date():
    due_date = "2024-03-25T16:00:00-04:00"

    assert "03/25/2024 - 04:00PM EDT" == search.format_date(due_date)


def test_format_set_aside_yes():
    set_asides = [{"code": "SBA", "desc": "Total SB"}]

    assert "Total SB" == search.format_set_aside("SBA", set_asides)


def test_build_textblock():
    assert {
        "type": "TextBlock",
        "text": "Test",
        "wrap": True,
    } == search.build_textblock("Test")


def test_format_set_aside_no():
    set_asides = [{"code": "SBA", "desc": "Total SB"}]

    assert search.format_set_aside(None, set_asides) is None


def test_format_results_one():
    raw_results = [
        {
            "title": "Test title",
            "agency": "DEPT OF DEFENSE.DEPT OF THE AIR FORCE.AIR FORCE MATERIEL COMMAND.AIR FORCE SUSTAINMENT CENTER.FA8522  AFSC PZABB",
            "posted_date": "2024-02-25",
            "type": "Solicitation",
            "set_aside": None,
            "due_date": "2024-03-25T16:00:00-04:00",
            "naics": "541511",
            "url": "https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view",
            "index": 1,
        }
    ]

    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** 1 new record. Displaying 1.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "1. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    config = {
        "agencies": [
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }

    assert items == search.format_results(raw_results, config, 1)


def test_format_results():
    raw_results = [
        {
            "title": "Test title",
            "agency": "DEPT OF DEFENSE.DEPT OF THE AIR FORCE.AIR FORCE MATERIEL COMMAND.AIR FORCE SUSTAINMENT CENTER.FA8522  AFSC PZABB",
            "posted_date": "2024-02-25",
            "type": "Solicitation",
            "set_aside": None,
            "due_date": "2024-03-25T16:00:00-04:00",
            "naics": "541511",
            "url": "https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view",
            "index": 1,
        },
        {
            "title": "Test title",
            "agency": "ENERGY, DEPARTMENT OF.ENERGY, DEPARTMENT OF.NNSA NON-MO CNTRCTNG OPS DIV",
            "posted_date": "2024-02-25",
            "type": "Special Notice",
            "set_aside": "SBA",
            "due_date": "2024-03-12T23:59:00-04:00",
            "naics": "541511",
            "url": "https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view",
            "index": 2,
        },
    ]

    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** 2 new records. Displaying 1 to 2.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "1. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "2. **Energy:** [Test title](https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/12/2024 - 11:59PM EDT | **Type:** Special Notice | **Set Aside:** Total SB | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    config = {
        "agencies": [
            {"agency": "ENERGY, DEPARTMENT OF", "abbr": "Energy"},
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }

    assert items == search.format_results(raw_results, config, 2)


def test_process_search_less_40(mocker):
    raw_results = [
        {
            "title": "Test title",
            "agency": "DEPT OF DEFENSE.DEPT OF THE AIR FORCE.AIR FORCE MATERIEL COMMAND.AIR FORCE SUSTAINMENT CENTER.FA8522  AFSC PZABB",
            "posted_date": "2024-02-25",
            "type": "Solicitation",
            "set_aside": None,
            "due_date": "2024-03-25T16:00:00-04:00",
            "naics": "541511",
            "url": "https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view",
        },
        {
            "title": "Test title",
            "agency": "ENERGY, DEPARTMENT OF.ENERGY, DEPARTMENT OF.NNSA NON-MO CNTRCTNG OPS DIV",
            "posted_date": "2024-02-25",
            "type": "Special Notice",
            "set_aside": "SBA",
            "due_date": "2024-03-12T23:59:00-04:00",
            "naics": "541511",
            "url": "https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view",
        },
    ]

    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** 2 new records. Displaying 1 to 2.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "1. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "2. **Energy:** [Test title](https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/12/2024 - 11:59PM EDT | **Type:** Special Notice | **Set Aside:** Total SB | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    config = {
        "from_days_back": 1,
        "naics": [{"code": 541511}],
        "agencies": [
            {"agency": "ENERGY, DEPARTMENT OF", "abbr": "Energy"},
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }

    mocker.patch("search.search", return_value=raw_results)
    assert [items] == search.process_search(api_client, "abcd", config)


def test_process_search_zero(mocker):
    raw_results = []
    config = {
        "from_days_back": 1,
        "naics": [{"code": 541511}],
        "agencies": [
            {"agency": "ENERGY, DEPARTMENT OF", "abbr": "Energy"},
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }

    mocker.patch("search.search", return_value=raw_results)
    assert [] == search.process_search(api_client, "abcd", config)


def test_teams_post(mocker):
    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** 2 new records. Displaying 1 to 2.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "1. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "2. **Energy:** [Test title](https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/12/2024 - 11:59PM EDT | **Type:** Special Notice | **Set Aside:** Total SB | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    body = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.0",
                    "body": [{"type": "Container", "items": items}],
                    "msteams": {"width": "Full"},
                },
            }
        ],
    }
    mock_teams_post = mocker.patch("search.client.MsApi.teams_post")
    search.teams_post(api_client, items)
    mock_teams_post.assert_called_once_with(body=body)
