"""
Tests for results.py
"""

from sam_search import results


def test_format_agency_two_str_match():
    agency = "AGENCY1.AGENCY2"
    agencies = [{"agency": "AGENCY2", "abbr": "ABBR"}]

    assert "ABBR" == results.format_agency(agency, agencies)


def test_format_agency_one_str_match():
    agency = "AGENCY1"
    agencies = [{"agency": "AGENCY1", "abbr": "ABBR"}]

    assert "ABBR" == results.format_agency(agency, agencies)


def test_format_agency_two_str_no_match():
    agency = "AGENCY1.AGENCY2"
    agencies = [{"agency": "FOO", "abbr": "ABBR"}]

    assert "AGENCY2" == results.format_agency(agency, agencies)


def test_format_agency_departmental_match():
    agency = "AGENCY1.DEPARTMENTAL OFFICES"
    agencies = [{"agency": "AGENCY1", "abbr": "ABBR"}]

    assert "ABBR" == results.format_agency(agency, agencies)


def test_format_date_posted_date():
    posted_date = "2024-02-25"

    assert "02/25/2024" == results.format_date(posted_date)


def test_format_date_due_date():
    due_date = "2024-03-25T16:00:00-04:00"

    assert "03/25/2024 - 04:00PM EDT" == results.format_date(due_date)


def test_format_set_aside_yes():
    set_asides = [{"code": "SBA", "desc": "Total SB"}]

    assert "Total SB" == results.format_set_aside("SBA", set_asides)


def test_format_set_aside_no():
    set_asides = [{"code": "SBA", "desc": "Total SB"}]

    assert results.format_set_aside(None, set_asides) is None
