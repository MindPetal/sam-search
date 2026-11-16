"""
Call the SAM.gov get opportunities search API.
"""

import logging

import client
from client.rest import ApiException

log = logging.getLogger(__name__)


def search(
    api_client: client.ApiClient,
    api_key: str,
    from_date: str,
    to_date: str,
    limit: int,
    naics: str,
) -> list[dict]:
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
        raise

    return api_response.to_dict()["value"]
