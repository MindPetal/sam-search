"""
Run the NAICS searches and post the results to the chat channel.
"""

import logging
import time
from datetime import date, timedelta

import client
from sam_search import sam, teams
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

    log.info("Posting results")

    for message in teams.format_results(records, config):
        teams.post(settings.ms_webhook_url, message)
        time.sleep(30)
