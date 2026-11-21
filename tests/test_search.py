"""
Tests for search.py
"""

import pytest
from conftest import make_record

from client.rest import ApiException
from sam_search import search, slack, teams
from sam_search.config import Settings

SAM_SEARCH = "sam_search.sam.search"


def test_process_search_less_40(mocker, api_client, config):
    records = [make_record(1), make_record(2)]
    mock_search = mocker.patch(SAM_SEARCH, return_value=records)

    result, errors = search.process_search(api_client, "abcd", config)

    mock_search.assert_called_once()
    assert mock_search.call_args.args[1] == "abcd"
    assert mock_search.call_args.args[4:] == (1000, 541511)
    assert result == [{**make_record(1), "index": 1}, {**make_record(2), "index": 2}]
    assert errors == []


def test_process_search_numbers_across_naics(mocker, api_client, config):
    config["naics"] = [{"code": 541511}, {"code": 541512}]
    mocker.patch(
        SAM_SEARCH, side_effect=[[make_record(1)], [make_record(2), make_record(3)]]
    )

    result, _ = search.process_search(api_client, "abcd", config)

    assert [r["index"] for r in result] == [1, 2, 3]


def test_process_search_zero(mocker, api_client, config):
    mocker.patch(SAM_SEARCH, return_value=[])

    assert ([], []) == search.process_search(api_client, "abcd", config)


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
    mocker.patch("sam_search.search.process_search", return_value=(records, []))
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
    mocker.patch("sam_search.search.process_search", return_value=([], []))
    mock_post = mocker.patch("sam_search.teams.post")

    search.main(settings(config))

    mock_post.assert_not_called()


SLACK_URL = "https://hooks.slack.com/services/T/B/X"


def test_main_posts_to_slack_only(mocker, config):
    records = [{**make_record(1), "index": 1}]
    mocker.patch("sam_search.search.process_search", return_value=(records, []))
    mock_teams_post = mocker.patch("sam_search.teams.post")
    mock_slack_format = mocker.patch(
        "sam_search.slack.format_results", return_value=[["blocks 1"], ["blocks 2"]]
    )
    mock_slack_post = mocker.patch("sam_search.slack.post")
    mocker.patch("sam_search.search.time.sleep")

    search.main(settings(config, ms_webhook_url="", slack_webhook_url=SLACK_URL))

    mock_teams_post.assert_not_called()
    mock_slack_format.assert_called_once_with(records, config, [])
    assert [c.args for c in mock_slack_post.call_args_list] == [
        (SLACK_URL, ["blocks 1"]),
        (SLACK_URL, ["blocks 2"]),
    ]


def test_main_teams_failure_still_posts_slack(mocker, config):
    records = [{**make_record(1), "index": 1}]
    mocker.patch("sam_search.search.process_search", return_value=(records, []))
    mocker.patch("sam_search.teams.format_results", return_value=[["message"]])
    mocker.patch("sam_search.teams.post", side_effect=Exception("boom"))
    mocker.patch("sam_search.slack.format_results", return_value=[["blocks"]])
    mock_slack_post = mocker.patch("sam_search.slack.post")
    mocker.patch("sam_search.search.time.sleep")

    with pytest.raises(RuntimeError, match="Posting failed for: teams"):
        search.main(settings(config, slack_webhook_url=SLACK_URL))

    mock_slack_post.assert_called_once_with(SLACK_URL, ["blocks"])


SAM_ERROR = {"status": 429, "message": "Too Many Requests"}

SAM_ERROR_TEXT = (
    "⚠️ There was an error calling the SAM.gov API during the workflow run."
    " HTTP 429 received: Too Many Requests."
)


def test_process_search_continues_after_api_error(mocker, api_client, config):
    config["naics"] = [{"code": 541511}, {"code": 541512}]
    mocker.patch(
        SAM_SEARCH,
        side_effect=[
            ApiException(status=429, reason="Too Many Requests"),
            [make_record(1)],
        ],
    )

    result, errors = search.process_search(api_client, "abcd", config)

    assert result == [{**make_record(1), "index": 1}]
    assert errors == [SAM_ERROR]


def test_process_search_uses_standard_reason_when_blank(mocker, api_client, config):
    mocker.patch(SAM_SEARCH, side_effect=ApiException(status=503, reason=""))

    _, errors = search.process_search(api_client, "abcd", config)

    assert errors == [{"status": 503, "message": "Service Unavailable"}]


def test_process_search_reraises_without_http_response(mocker, api_client, config):
    # Status 0 means no HTTP response (e.g. an SSL error). Its text can include
    # the request URL and API key, so it isn't posted.
    mocker.patch(
        SAM_SEARCH, side_effect=ApiException(status=0, reason="SSLError ?api_key=abcd")
    )

    with pytest.raises(ApiException):
        search.process_search(api_client, "abcd", config)


def test_main_posts_api_error_then_fails(mocker, config):
    # With no records, the error note is still posted, then the run fails
    mocker.patch("sam_search.search.process_search", return_value=([], [SAM_ERROR]))
    mock_teams_post = mocker.patch("sam_search.teams.post")
    mock_slack_post = mocker.patch("sam_search.slack.post")
    mocker.patch("sam_search.search.time.sleep")

    with pytest.raises(RuntimeError, match=r"^SAM.gov API returned HTTP errors: 429$"):
        search.main(settings(config, slack_webhook_url=SLACK_URL))

    teams_message = mock_teams_post.call_args.args[1]
    slack_message = mock_slack_post.call_args.args[1]
    assert [item["text"] for item in teams_message] == [SAM_ERROR_TEXT]
    assert [block["text"] for block in slack_message] == [SAM_ERROR_TEXT]


def test_error_note_follows_record_messages(config):
    records = [{**make_record(1), "index": 1}]

    for channel in (teams, slack):
        messages = channel.format_results(records, config, [SAM_ERROR])

        assert len(messages) == 2
        assert messages[-1][0]["text"] == SAM_ERROR_TEXT


def test_error_note_lists_each_distinct_error_once(config):
    errors = [SAM_ERROR, SAM_ERROR, {"status": 500, "message": "Internal Server Error"}]

    [[item]] = teams.format_results([], config, errors)

    assert item["text"] == (
        f"{SAM_ERROR_TEXT}\n\n"
        "⚠️ There was an error calling the SAM.gov API during the workflow run."
        " HTTP 500 received: Internal Server Error."
    )
