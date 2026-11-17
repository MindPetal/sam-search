"""
Tests for slack.py
"""

from datetime import date

import pytest
from conftest import make_record

from sam_search import results, slack


def numbered(count: int) -> list[dict]:
    return [{**make_record(n), "index": n} for n in range(1, count + 1)]


def cell_text(cell: dict) -> str:
    return "".join(e["text"] for e in cell["elements"][0]["elements"])


def test_format_message(config):
    records = numbered(2)

    blocks = slack.format_message(records, config, 2)

    assert [block["type"] for block in blocks] == ["markdown", "table"]
    assert blocks[0]["text"] == (
        f"**{date.today().strftime('%A, %m/%d/%Y')}.** 2 new records."
        " Displaying 1 to 2."
    )
    # One wrapped row per record, the same text as Teams
    table = blocks[1]
    assert table["column_settings"] == [{"is_wrapped": True}]
    assert [cell_text(row[0]) for row in table["rows"]] == [
        cell_text(slack.build_cell(results.record_content(r, config))) for r in records
    ]
    elements = table["rows"][0][0]["elements"][0]["elements"]
    assert {"type": "text", "text": "Energy:", "style": {"bold": True}} in elements
    assert {
        "type": "link",
        "text": "Test title 1",
        "url": "https://sam.gov/opp/1/view",
    } in elements


def test_format_results_splits_every_20_records(config):
    today = date.today().strftime("%A, %m/%d/%Y")

    messages = slack.format_results(numbered(45), config)

    assert [[b["type"] for b in m] for m in messages] == [["markdown", "table"]] * 3
    assert [len(m[1]["rows"]) for m in messages] == [20, 20, 5]
    assert [m[0]["text"] for m in messages] == [
        f"**{today}.** 45 new records. Displaying 1 to 20.",
        f"**{today} continued.** Displaying 21 to 40.",
        f"**{today} continued.** Displaying 41 to 45.",
    ]
    # Each message's table fits Slack's limit, so it isn't split further
    assert all(len(slack.split_messages(m)) == 1 for m in messages)


def test_build_cell_keeps_bold_and_links():
    cell = slack.build_cell("1. **Energy:** [Title](https://sam.gov/opp/1) | A & B")

    assert cell["elements"][0]["elements"] == [
        {"type": "text", "text": "1. "},
        {"type": "text", "text": "Energy:", "style": {"bold": True}},
        {"type": "text", "text": " "},
        {"type": "link", "text": "Title", "url": "https://sam.gov/opp/1"},
        {"type": "text", "text": " | A & B"},
    ]


def test_build_tables_splits_long_tables():
    tables = slack.build_tables(["x" * 1_000] * 25)

    assert [len(t["rows"]) for t in tables] == [10, 10, 5]
    assert all(slack.table_chars(t) <= slack.MAX_TABLE_CHARS for t in tables)


def test_split_messages_one_table_per_message():
    table = slack.build_tables(["a"])[0]

    messages = slack.split_messages([block("header"), table, table])

    assert [[b["type"] for b in m] for m in messages] == [
        ["markdown", "table"],
        ["table"],
    ]


def test_fallback_text_from_table():
    table = slack.build_tables(["\u200b1. **Energy:** [Title](https://x)"])[0]

    assert slack.fallback_text([table]) == "1. Energy: Title"


def test_format_results_empty(config):
    assert slack.format_results([], config) == []


def block(text: str) -> dict:
    return {"type": "markdown", "text": text}


def test_split_messages_by_block_count():
    messages = slack.split_messages([block("x")] * 120)

    assert [len(m) for m in messages] == [50, 50, 20]


def test_split_messages_by_character_limit():
    messages = slack.split_messages([block("x" * 5_000)] * 5)

    assert [len(m) for m in messages] == [2, 2, 1]


def test_build_markdown_truncates_oversized_text():
    text = slack.build_markdown("x" * 20_000)["text"]

    assert len(text) == slack.MAX_MARKDOWN_CHARS
    assert text.endswith("…")


class FakeResponse:
    def __init__(self, status: int, data: bytes = b"ok"):
        self.status = status
        self.data = data


def test_post(mocker):
    mock_request = mocker.patch(
        "urllib3.PoolManager.request", return_value=FakeResponse(200)
    )
    blocks = [block("**Monday, 11/16/2026.** 1 new record. Displaying 1."), block("x")]

    slack.post("https://hooks.slack.com/services/T/B/X", blocks)

    args, kwargs = mock_request.call_args
    assert args == ("POST", "https://hooks.slack.com/services/T/B/X")
    assert kwargs["json"] == {
        "text": "Monday, 11/16/2026. 1 new record. Displaying 1.",
        "blocks": blocks,
    }


def test_post_raises_on_error(mocker):
    mocker.patch(
        "urllib3.PoolManager.request",
        return_value=FakeResponse(403, b"action_prohibited"),
    )

    with pytest.raises(slack.SlackPostError, match="403: action_prohibited"):
        slack.post("https://hooks.slack.com/services/T/B/X", [block("x")])
