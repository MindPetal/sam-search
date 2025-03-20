"""
    Script executes via github actions to call 
    sam.gov opportunities API and post results to MS Teams. 
"""

import logging
import sys
from datetime import date, datetime, timedelta, timezone
from itertools import zip_longest
from zoneinfo import ZoneInfo

import yaml

import client
from client.rest import ApiException

log = logging.getLogger("search")
logging.basicConfig(level=logging.INFO)


def load_config():
    # Load yaml config file
    with open("config.yaml", "r") as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def search(api_client, api_key, from_date, to_date, limit, naics):
    # Execute sam.gov search
    api_instance = client.SamApi(api_client)

    try:
        api_response = api_instance.search(
            api_key=api_key,
            posted_from=from_date,
            posted_to=to_date,
            limit=limit,
            naics=naics,
        )
    except ApiException as e:
        log.exception("Exception when calling SamApi->search: %s\n" % e)

    return api_response.to_dict()["value"]


def format_agency(agency, agencies):
    # Formats the agency name for display
    sam_agency = agency.split(".")
    agency_substr = ""
    agency_display = ""

    if len(sam_agency) > 1:

        if sam_agency[1] in (
            "DEPARTMENTAL OFFICES",
            "OFFICE OF THE SECRETARY",
            "OFFICE OF THE COMPTROLLER OF THE CURRENCY",
            "IMMEDIATE OFFICE OF THE SECRETARY OF DEFENSE",
            "OFFICE OF INSPECTOR GENERAL",
            "OFFICE OF THE INSPECTOR GENERAL",
        ):
            agency_substr = sam_agency[0]
        else:
            agency_substr = sam_agency[1]

    else:
        agency_substr = sam_agency[0]

    agency_dict = next(
        (name for name in agencies if agency_substr == name["agency"]), None
    )

    if bool(agency_dict):
        agency_display = agency_dict["abbr"]
    else:
        agency_display = agency_substr

    return agency_display


def format_date(raw_date):
    # Format date/times to nice format
    formatted_date = None

    if bool(raw_date):

        if "T" in raw_date:
            date_obj = datetime.fromisoformat(raw_date).astimezone(timezone.utc)
            date_obj = date_obj.astimezone(ZoneInfo("America/New_York"))
            formatted_date = date_obj.strftime("%m/%d/%Y - %I:%M%p %Z")
        else:
            formatted_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime(
                "%m/%d/%Y"
            )

    return formatted_date


def format_set_aside(set_aside, set_asides):
    # Format set-aside type for display

    if bool(set_aside):
        set_aside = next(
            (code for code in set_asides if set_aside == code["code"]), None
        )["desc"]

    return set_aside


def format_results(raw_results, config, total):
    # Format results string

    if raw_results[0]["index"] == 1:
        result_string = f'**{date.today().strftime("%A, %m/%d/%Y")}.** {total} new records. Displaying {raw_results[0]["index"]} to {raw_results[-1]["index"]}.'
    else:
        result_string = f'**{date.today().strftime("%A, %m/%d/%Y")} continued.** Displaying {raw_results[0]["index"]} to {raw_results[-1]["index"]}.'

    for result in raw_results:
        result_string += "\n\n"

        agency = None

        if bool(result["agency"]):
            agency = format_agency(result["agency"], config["agencies"])

        result_string += f'\u2705 **{result["index"]}. {agency}: [{result["title"]}]({result["url"]})**'

        result_string += f'\n\n**Date:** {format_date(result["posted_date"])} | **Due:** {format_date(result["due_date"])} | '

        set_aside = format_set_aside(result["set_aside"], config["set_asides"])
        result_string += f'**Type:** {result["type"]} | **Set Aside:** {set_aside} | **NAICS:** {result["naics"]}'

    return result_string


def process_search(api_client, sam_api_key, config):
    # Prepare sam.gov search and format results
    raw_results = []
    formatted_results = []
    limit = 1000
    from_days_back = config["from_days_back"]
    from_date = (date.today() - timedelta(days=from_days_back)).strftime("%m/%d/%Y")
    to_date = date.today().strftime("%m/%d/%Y")

    for naics in config["naics"]:
        naics_result = search(
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

    # Teams has a message limit of 28kb so need to divide into multiple lists
    if record_cnt > 40:
        split_results = list(zip_longest(*[iter(raw_results)] * 40, fillvalue=None))

        for results in split_results:
            results = [result for result in results if result is not None]
            formatted_results.append(format_results(results, config, record_cnt))
    elif 0 < record_cnt <= 40:
        formatted_results.append(format_results(raw_results, config, record_cnt))

    return formatted_results


def teams_post(api_client, content):
    # Execute MS Teams post
    api_instance = client.MsApi(api_client)

    try:
        api_instance.teams_post(
            body={
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.0",
                            "body": [
                                {
                                    "type": "Container",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Thursday, 03/20/2025. 2 new records. Displaying 1 to 2.\n\n1. **Test: [Test](https://test.com)**\n\n   **Date:** 03/19/2025 | **Due:** 03/26/2025 - 11:59AM EDT | **Type:** Test | **Set Aside:** Test | **NAICS:** 123456",
                                            "wrap": True,
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": "",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": "2. **Test: [Test](https://test.com)**\n\n   **Date:** 03/19/2025 | **Due:** 03/26/2025 - 11:59AM EDT | **Type:** Test | **Set Aside:** Test | **NAICS:** 123456",
                                            "wrap": True,
                                        }
                                    ],
                                }
                            ],
                            "msteams": {"width": "Full"},
                        },
                    }
                ],
            }
        )

    except ApiException as e:
        log.exception("Exception when calling MsApi->teams_post: %s\n" % e)


def main(sam_api_key, ms_webhook_url):
    # Primary processing fuction

    log.info("Start processing, load config data")
    config = load_config()
    api_config = client.Configuration()
    api_config.host = config["sam_url"]
    api_client = client.ApiClient(api_config)

    log.info("Process search")
    search_results = process_search(api_client, sam_api_key, config)

    log.info("Process Teams posts")
    api_config.host = ms_webhook_url

    for result in search_results:
        teams_post(api_client, result)


""" Read in sam_api_key, ms_webhook_url.
"""
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
