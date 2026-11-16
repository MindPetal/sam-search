"""
Tests for teams.py
"""

from datetime import date

from conftest import make_record

import client
from sam_search import teams


def test_build_textblock():
    assert {
        "type": "TextBlock",
        "text": "Test",
        "wrap": True,
    } == teams.build_textblock("Test")


def test_format_message_one():
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
            "text": f"**{date.today().strftime('%A, %m/%d/%Y')}.** 1 new record. Displaying 1.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "Table",
            "columns": [{"width": 1}],
            "firstRowAsHeaders": False,
            "gridStyle": "default",
            "rows": [
                {
                    "type": "TableRow",
                    "style": "default",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "\u200b1. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n**Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
                                    "wrap": True,
                                }
                            ],
                        },
                    ],
                },
            ],
        },
    ]

    config = {
        "agencies": [
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }

    assert items == teams.format_message(raw_results, config, 1)


def test_format_message():
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
            "text": f"**{date.today().strftime('%A, %m/%d/%Y')}.** 2 new records. Displaying 1 to 2.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "Table",
            "columns": [{"width": 1}],
            "firstRowAsHeaders": False,
            "gridStyle": "default",
            "rows": [
                {
                    "type": "TableRow",
                    "style": "default",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "\u200b1. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n**Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
                                    "wrap": True,
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "TableRow",
                    "style": "emphasis",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "\u200b2. **Energy:** [Test title](https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view)\n\n**Date:** 02/25/2024 | **Due:** 03/12/2024 - 11:59PM EDT | **Type:** Special Notice | **Set Aside:** Total SB | **NAICS:** 541511",
                                    "wrap": True,
                                }
                            ],
                        },
                    ],
                },
            ],
        },
    ]

    config = {
        "agencies": [
            {"agency": "ENERGY, DEPARTMENT OF", "abbr": "Energy"},
            {"agency": "DEPT OF THE AIR FORCE", "abbr": "Air Force"},
        ],
        "set_asides": [{"code": "SBA", "desc": "Total SB"}],
    }

    assert items == teams.format_message(raw_results, config, 2)


def test_post(mocker):
    items = [
        {
            "type": "TextBlock",
            "text": f"**{date.today().strftime('%A, %m/%d/%Y')}.** 2 new records. Displaying 1 to 2.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "1\\. **Air Force:** [Test title](https://sam.gov/opp/bc92c9b1d0944b11b05d719c4f5dc863/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/25/2024 - 04:00PM EDT | **Type:** Solicitation | **Set Aside:** None | **NAICS:** 541511",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "2\\. **Energy:** [Test title](https://sam.gov/opp/84bfc6e3413e487db821841c9ab4701c/view)\n\n- **Date:** 02/25/2024 | **Due:** 03/12/2024 - 11:59PM EDT | **Type:** Special Notice | **Set Aside:** Total SB | **NAICS:** 541511",
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
                    "version": "1.5",
                    "body": [{"type": "Container", "items": items}],
                    "msteams": {"width": "Full"},
                },
            }
        ],
    }
    mock_teams_post = mocker.patch.object(client.MsApi, "teams_post", autospec=True)
    teams.post("https://webhook.example.com", items)
    mock_teams_post.assert_called_once()
    api_instance = mock_teams_post.call_args.args[0]
    assert api_instance.api_client.configuration.host == "https://webhook.example.com"
    assert mock_teams_post.call_args.kwargs == {"body": body}


def numbered(count: int) -> list[dict]:
    return [{**make_record(n), "index": n} for n in range(1, count + 1)]


def header(message: list[dict]) -> str:
    return message[0]["text"]


def test_format_results_single_message(config):
    records = numbered(2)

    assert teams.format_results(records, config) == [
        teams.format_message(records, config, 2)
    ]


def test_format_results_splits_every_40_records(config):
    today = date.today().strftime("%A, %m/%d/%Y")

    messages = teams.format_results(numbered(85), config)

    assert [len(m[2]["rows"]) for m in messages] == [40, 40, 5]
    assert [header(m) for m in messages] == [
        f"**{today}.** 85 new records. Displaying 1 to 40.",
        f"**{today} continued.** Displaying 41 to 80.",
        f"**{today} continued.** Displaying 81 to 85.",
    ]


def test_format_results_empty(config):
    assert teams.format_results([], config) == []
