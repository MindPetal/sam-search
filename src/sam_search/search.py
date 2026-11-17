"""
Run the NAICS searches and post the results to the configured chat channels
(MS Teams and/or Slack).
"""

import logging
import time
from datetime import date, timedelta

import client
from sam_search import sam, slack, teams
from sam_search.config import Settings

log = logging.getLogger(__name__)


def process_search(
    api_client: client.ApiClient, sam_api_key: str, config: dict
) -> list[dict]:
    # Run sam.gov searches and return all records, numbered from 1
    raw_results = []
    limit = 1000
    from_days_back = config["from_days_back"]
    from_date = (date.today() - timedelta(days=from_days_back)).strftime("%m/%d/%Y")
    to_date = date.today().strftime("%m/%d/%Y")

    for naics in config["naics"]:
        naics_result = sam.search(
            api_client, sam_api_key, from_date, to_date, limit, naics["code"]
        )

        for result in naics_result:
            raw_results.append(result)

    # Inject index into each record
    n = 1

    for result in raw_results:
        result["index"] = n
        n += 1

    record_cnt = len(raw_results)
    log.info(f"Total records: {record_cnt}")

    return raw_results


def main(settings: Settings) -> None:
    # Primary processing function

    log.info("Start processing, load config data")
    config = settings.config

    api_config = client.Configuration()
    api_config.host = config["sam_url"]
    api_client = client.ApiClient(api_config)

    log.info("Process search")
    records = process_search(api_client, settings.sam_api_key, config)

    post_results(settings, records)


def post_results(settings: Settings, records: list[dict]) -> None:
    # Post to every configured chat channel. A failure on one channel doesn't
    # stop the others, but the run still fails afterwards.
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
            for message in channel.format_results(records, settings.config):
                channel.post(webhook_url, message)
                time.sleep(30)
        except Exception:
            log.exception("Posting results to %s failed", name)
            failed.append(name)

    if failed:
        raise RuntimeError(f"Posting failed for: {', '.join(failed)}")
