"""
Build MS Teams Adaptive Card content and post it to a Teams webhook.

Each chat destination gets its own module with the same interface:
format_results(records, config, errors) -> one list of items per message, and
post(webhook_url, items).
"""

import logging

import client
from client.rest import ApiException
from sam_search import results

log = logging.getLogger(__name__)

MAX_RECORDS_PER_MESSAGE = 40


def build_textblock(content: str) -> dict:
    # Build TextBlock for MS Teams
    return {"type": "TextBlock", "text": content, "wrap": True}


def build_row(content: str, stripe_index: int) -> dict:
    # Build a striped single-cell TableRow
    return {
        "type": "TableRow",
        "style": "emphasis" if stripe_index % 2 else "default",
        "cells": [
            {"type": "TableCell", "items": [build_textblock(content)]},
        ],
    }


def format_message(raw_results: list[dict], config: dict, total: int) -> list:
    # Format one message's results into a striped Adaptive Card table

    header = results.header_text(
        raw_results[0]["index"], raw_results[-1]["index"], total
    )
    rows = [
        build_row(results.record_content(result, config), stripe_index)
        for stripe_index, result in enumerate(raw_results)
    ]

    table = {
        "type": "Table",
        "columns": [{"width": 1}],
        "firstRowAsHeaders": False,
        "gridStyle": "default",
        "rows": rows,
    }

    return [build_textblock(header), build_textblock(""), table]


def format_results(
    records: list[dict], config: dict, errors: list[dict] | None = None
) -> list[list[dict]]:
    # Format results into one list of card items per Teams message, then a
    # final message for any SAM.gov errors
    messages = []
    record_cnt = len(records)

    # Teams has a message limit of 28kb so need to divide into multiple lists
    for start in range(0, record_cnt, MAX_RECORDS_PER_MESSAGE):
        chunk = records[start : start + MAX_RECORDS_PER_MESSAGE]
        messages.append(format_message(chunk, config, record_cnt))

    if errors:
        messages.append([build_textblock(results.sam_errors(errors))])

    return messages


def post(webhook_url: str, items: list[dict]) -> None:
    # Execute MS Teams post
    api_config = client.Configuration()
    api_config.host = webhook_url
    api_instance = client.MsApi(client.ApiClient(api_config))

    try:
        api_instance.teams_post(
            body={
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
        )

    except ApiException as e:
        log.exception("Exception when calling MsApi->teams_post: %s\n" % e)
        raise
