"""
Turn SAM.gov opportunity fields into display values and the Markdown text
shared by every chat channel.
"""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


def format_agency(agency: str, agencies: list[dict]) -> str:
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
            "OFFICE OF JUSTICE PROGRAMS",
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


def format_date(raw_date: str) -> str | None:
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


def format_set_aside(set_aside: str | None, set_asides: list[dict]) -> str | None:
    # Format set-aside type for display

    if bool(set_aside) and set_aside.upper() != "NONE":
        match = next((code for code in set_asides if set_aside == code["code"]), None)
        if match is not None:
            set_aside = match["desc"]

    return set_aside


def header_text(first_index: int, last_index: int, total: int) -> str:
    # Message header: record count and which records this message displays
    today = date.today().strftime("%A, %m/%d/%Y")

    if first_index != 1:
        return f"**{today} continued.** Displaying {first_index} to {last_index}."

    if total == 1:
        return f"**{today}.** {total} new record. Displaying {first_index}."

    return (
        f"**{today}.** {total} new records. Displaying {first_index} to {last_index}."
    )


def record_content(result: dict, config: dict) -> str:
    # Markdown for one opportunity: agency and linked title, then its details
    agency = None

    if bool(result["agency"]):
        agency = format_agency(result["agency"], config["agencies"])

    content = (
        f"\u200b{result['index']}. **{agency}:** [{result['title']}]({result['url']})"
    )

    content += f"\n\n**Date:** {format_date(result['posted_date'])} | **Due:** {format_date(result['due_date'])} | "

    set_aside = format_set_aside(result["set_aside"], config["set_asides"])
    content += f"**Type:** {result['type']} | **Set Aside:** {set_aside} | **NAICS:** {result['naics']}"

    return content
