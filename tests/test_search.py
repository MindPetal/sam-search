"""
Tests for search.py
"""

import pytest
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


def settings(
    config: dict,
    ms_webhook_url: str = "https://webhook.example.com",
    slack_webhook_url: str = "",
) -> Settings:
    return Settings(
        sam_api_key="abcd",
        ms_webhook_url=ms_webhook_url,
        config=config,
        slack_webhook_url=slack_webhook_url,
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


SLACK_URL = "https://hooks.slack.com/services/T/B/X"


def test_main_posts_to_slack_only(mocker, config):
    records = [{**make_record(1), "index": 1}]
    mocker.patch("sam_search.search.process_search", return_value=records)
    mock_teams_post = mocker.patch("sam_search.teams.post")
    mock_slack_format = mocker.patch(
        "sam_search.slack.format_results", return_value=[["blocks 1"], ["blocks 2"]]
    )
    mock_slack_post = mocker.patch("sam_search.slack.post")
    mocker.patch("sam_search.search.time.sleep")

    search.main(settings(config, ms_webhook_url="", slack_webhook_url=SLACK_URL))

    mock_teams_post.assert_not_called()
    mock_slack_format.assert_called_once_with(records, config)
    assert [c.args for c in mock_slack_post.call_args_list] == [
        (SLACK_URL, ["blocks 1"]),
        (SLACK_URL, ["blocks 2"]),
    ]


def test_main_teams_failure_still_posts_slack(mocker, config):
    records = [{**make_record(1), "index": 1}]
    mocker.patch("sam_search.search.process_search", return_value=records)
    mocker.patch("sam_search.teams.format_results", return_value=[["message"]])
    mocker.patch("sam_search.teams.post", side_effect=Exception("boom"))
    mocker.patch("sam_search.slack.format_results", return_value=[["blocks"]])
    mock_slack_post = mocker.patch("sam_search.slack.post")
    mocker.patch("sam_search.search.time.sleep")

    with pytest.raises(RuntimeError, match="Posting failed for: teams"):
        search.main(settings(config, slack_webhook_url=SLACK_URL))

    mock_slack_post.assert_called_once_with(SLACK_URL, ["blocks"])
