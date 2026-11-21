"""
Build Slack Block Kit messages and post them to a Slack incoming webhook.

Each chat destination gets its own module with the same interface:
format_results(records, config, errors) -> one list of items per message, and
post(webhook_url, items).
"""

import re
import time

import certifi
import urllib3

from sam_search import results

# Slack limits per message: 50 blocks, 12,000 characters across all markdown
# blocks, and 10,000 characters across all table cells. Tables also allow at
# most 100 rows.
MAX_BLOCKS = 50
MAX_MARKDOWN_CHARS = 12_000
MAX_TABLE_CHARS = 10_000
MAX_TABLE_ROWS = 100

# Fewer than Teams' 40 so each message's table stays under the character limit
MAX_RECORDS_PER_MESSAGE = 20

# One table per message is always accepted. Raise this to group several
# tables into one message if your workspace allows it.
MAX_TABLES_PER_MESSAGE = 1

# **bold** or [text](url) in the shared Markdown text
MARKDOWN_TOKEN = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)")


class SlackPostError(Exception):
    pass


def build_markdown(text: str) -> dict:
    # Build a markdown block, which renders standard Markdown (**bold**,
    # [text](url))
    if len(text) > MAX_MARKDOWN_CHARS:
        text = text[: MAX_MARKDOWN_CHARS - 1] + "…"

    return {"type": "markdown", "text": text}


def build_cell(markdown: str) -> dict:
    # Build a rich text table cell from Markdown, keeping **bold** and
    # [text](url) links
    elements: list[dict] = []
    position = 0

    for match in MARKDOWN_TOKEN.finditer(markdown):
        if match.start() > position:
            elements.append(
                {"type": "text", "text": markdown[position : match.start()]}
            )

        bold, link_text, url = match.groups()

        if bold is not None:
            elements.append({"type": "text", "text": bold, "style": {"bold": True}})
        else:
            elements.append({"type": "link", "text": link_text, "url": url})

        position = match.end()

    if position < len(markdown) or not elements:
        elements.append({"type": "text", "text": markdown[position:] or " "})

    return {
        "type": "rich_text",
        "elements": [{"type": "rich_text_section", "elements": elements}],
    }


def cell_chars(cell: dict) -> int:
    # Characters a cell counts toward Slack's table limit. Link URLs are
    # included to stay on the safe side.
    return sum(
        len(element.get("text", "")) + len(element.get("url", ""))
        for section in cell["elements"]
        for element in section["elements"]
    )


def table_chars(table: dict) -> int:
    return sum(cell_chars(cell) for row in table["rows"] for cell in row)


def build_tables(contents: list[str]) -> list[dict]:
    # Build a single-column table with one wrapped row per record, the same
    # layout as the Teams card. Splits into more tables to stay within Slack's
    # table limits.
    tables: list[list[list[dict]]] = []
    rows: list[list[dict]] = []
    chars = 0

    for content in contents:
        row = [build_cell(content)]
        size = cell_chars(row[0])

        if rows and (len(rows) >= MAX_TABLE_ROWS or chars + size > MAX_TABLE_CHARS):
            tables.append(rows)
            rows, chars = [], 0

        rows.append(row)
        chars += size

    if rows:
        tables.append(rows)

    return [
        {"type": "table", "column_settings": [{"is_wrapped": True}], "rows": rows}
        for rows in tables
    ]


def format_message(raw_results: list[dict], config: dict, total: int) -> list:
    # Format one message's results: the header, then a table with one row per
    # record
    header = results.header_text(
        raw_results[0]["index"], raw_results[-1]["index"], total
    )

    return [build_markdown(header)] + build_tables(
        [results.record_content(result, config) for result in raw_results]
    )


def format_results(
    records: list[dict], config: dict, errors: list[dict] | None = None
) -> list[list[dict]]:
    # Format results into one list of blocks per Slack message, then a final
    # message for any SAM.gov errors
    messages = []
    record_cnt = len(records)

    for start in range(0, record_cnt, MAX_RECORDS_PER_MESSAGE):
        chunk = records[start : start + MAX_RECORDS_PER_MESSAGE]
        messages.append(format_message(chunk, config, record_cnt))

    if errors:
        messages.append([build_markdown(results.sam_errors(errors))])

    return messages


def split_messages(blocks: list[dict]) -> list[list[dict]]:
    # Group blocks into messages that stay within Slack's per-message limits
    messages: list[list[dict]] = []
    current: list[dict] = []
    markdown_chars = table_chars_total = tables = 0

    for block in blocks:
        is_table = block["type"] == "table"
        size = table_chars(block) if is_table else len(block["text"])

        if current and (
            len(current) >= MAX_BLOCKS
            or (is_table and tables >= MAX_TABLES_PER_MESSAGE)
            or (is_table and table_chars_total + size > MAX_TABLE_CHARS)
            or (not is_table and markdown_chars + size > MAX_MARKDOWN_CHARS)
        ):
            messages.append(current)
            current = []
            markdown_chars = table_chars_total = tables = 0

        current.append(block)

        if is_table:
            tables += 1
            table_chars_total += size
        else:
            markdown_chars += size

    if current:
        messages.append(current)

    return messages


def block_text(block: dict) -> str:
    # Plain text of a markdown block, or of a table's first cell
    if block["type"] == "table":
        section = block["rows"][0][0]["elements"][0]
        return "".join(element["text"] for element in section["elements"])

    return block["text"].replace("**", "")


def fallback_text(blocks: list[dict]) -> str:
    # Plain text used in notifications, from the message's first block
    return block_text(blocks[0]).strip("\u200b")[:150]


def post(webhook_url: str, items: list[dict]) -> None:
    # Execute Slack post, splitting into several messages when needed
    http = urllib3.PoolManager(ca_certs=certifi.where())

    for n, blocks in enumerate(split_messages(items)):
        if n:
            # Incoming webhooks allow about one message per second
            time.sleep(1)

        response = http.request(
            "POST",
            webhook_url,
            json={"text": fallback_text(blocks), "blocks": blocks},
            timeout=30,
        )

        if response.status != 200:
            body = response.data.decode(errors="replace")
            raise SlackPostError(
                f"Slack webhook returned HTTP {response.status}: {body}"
            )
