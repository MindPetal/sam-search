"""
Tests for search.py
"""

from conftest import make_record

from sam_search import search
from sam_search.config import Settings

SAM_SEARCH = "sam_search.sam.search"


def test_process_search_less_40(mocker, api_client, config):
    records = [make_record(1), make_record(2)]
    mock_search = mocker.patch(SAM_SEARCH, return_value=records)

    result = search.process_search(api_client, "abcd", config)

    mock_search.assert_called_once()
    assert mock_search.call_args.args[1] == "abcd"
    assert mock_search.call_args.args[4:] == (1000, 541511)
    assert result == [{**make_record(1), "index": 1}, {**make_record(2), "index": 2}]


def test_process_search_numbers_across_naics(mocker, api_client, config):
    config["naics"] = [{"code": 541511}, {"code": 541512}]
    mocker.patch(
        SAM_SEARCH, side_effect=[[make_record(1)], [make_record(2), make_record(3)]]
    )

    result = search.process_search(api_client, "abcd", config)

    assert [r["index"] for r in result] == [1, 2, 3]


def test_process_search_zero(mocker, api_client, config):
    mocker.patch(SAM_SEARCH, return_value=[])

    assert [] == search.process_search(api_client, "abcd", config)


def settings(config: dict) -> Settings:
    return Settings(
        sam_api_key="abcd",
        ms_webhook_url="https://webhook.example.com",
        config=config,
    )


def test_main_posts_each_message(mocker, config):
    records = [{**make_record(1), "index": 1}]
    mocker.patch("sam_search.search.process_search", return_value=records)
    mocker.patch(
        "sam_search.teams.format_results", return_value=[["message 1"], ["message 2"]]
    )
    mock_post = mocker.patch("sam_search.teams.post")
    mock_sleep = mocker.patch("sam_search.search.time.sleep")

    search.main(settings(config))

    assert [c.args for c in mock_post.call_args_list] == [
        ("https://webhook.example.com", ["message 1"]),
        ("https://webhook.example.com", ["message 2"]),
    ]
    assert mock_sleep.call_count == 2


def test_main_no_results(mocker, config):
    mocker.patch("sam_search.search.process_search", return_value=[])
    mock_post = mocker.patch("sam_search.teams.post")

    search.main(settings(config))

    mock_post.assert_not_called()
