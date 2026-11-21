"""
Run the NAICS searches and post the results to the configured chat channels
(MS Teams and/or Slack).
"""

import logging
import time
from datetime import date, timedelta
from http import HTTPStatus

import client
from client.rest import ApiException
from sam_search import sam, slack, teams
from sam_search.config import Settings

log = logging.getLogger(__name__)


def api_error(e: ApiException) -> dict:
    # Status and reason of a failed SAM.gov call.
    message = e.reason

    if not message:
        try:
            message = HTTPStatus(e.status).phrase
        except ValueError:
            message = "Unknown error"

    return {"status": e.status, "message": message}


def process_search(
    api_client: client.ApiClient, sam_api_key: str, config: dict
) -> tuple[list[dict], list[dict]]:
    # Run sam.gov searches and return all records, numbered from 1, and any
    # SAM.gov HTTP errors. An error on one NAICS code doesn't stop the others.
    raw_results = []
    errors = []
    limit = 1000
    from_days_back = config["from_days_back"]
    from_date = (date.today() - timedelta(days=from_days_back)).strftime("%m/%d/%Y")
    to_date = date.today().strftime("%m/%d/%Y")

    for naics in config["naics"]:
        try:
            naics_result = sam.search(
                api_client, sam_api_key, from_date, to_date, limit, naics["code"]
            )
        except ApiException as e:
            if not e.status:
                # No HTTP response (e.g. an SSL error), so nothing to report
                raise

            errors.append(api_error(e))
            continue

        for result in naics_result:
            raw_results.append(result)

    # Inject index into each record
    n = 1

    for result in raw_results:
        result["index"] = n
        n += 1

    record_cnt = len(raw_results)
    log.info(f"Total records: {record_cnt}")

    return raw_results, errors


def main(settings: Settings) -> None:
    # Primary processing function

    log.info("Start processing, load config data")
    config = settings.config

    api_config = client.Configuration()
    api_config.host = config["sam_url"]
    api_client = client.ApiClient(api_config)

    log.info("Process search")
    records, errors = process_search(api_client, settings.sam_api_key, config)

    post_results(settings, records, errors)


def post_results(
    settings: Settings, records: list[dict], errors: list[dict] | None = None
) -> None:
    # Post to every configured chat channel. A failure on one channel doesn't
    # stop the others, but the run still fails afterwards. SAM.gov errors are
    # included in the post and also fail the run.
    errors = errors or []
    channels = [
        (teams, settings.ms_webhook_url),
        (slack, settings.slack_webhook_url),
    ]
    failed = []

    for channel, webhook_url in channels:
        if not webhook_url:
            continue

        name = channel.__name__.rsplit(".", 1)[-1]
        log.info("Posting results to %s", name)

        try:
            for message in channel.format_results(records, settings.config, errors):
                channel.post(webhook_url, message)
                time.sleep(30)
        except Exception:
            log.exception("Posting results to %s failed", name)
            failed.append(name)

    problems = []

    if failed:
        problems.append(f"Posting failed for: {', '.join(failed)}")

    if errors:
        problems.append(
            "SAM.gov API returned HTTP errors: "
            + ", ".join(str(e["status"]) for e in errors)
        )

    if problems:
        raise RuntimeError("; ".join(problems))
