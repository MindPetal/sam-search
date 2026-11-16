"""
Turn SAM.gov opportunity fields into display values.
"""

from datetime import datetime, timezone
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
