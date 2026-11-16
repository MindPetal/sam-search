"""
Tests for sam.py
"""

import client
from sam_search import sam


def test_search(mocker, api_client):
    api_response = client.ODataValueOfIEnumerableOfOppDto()
    opp_dto = client.OppDto()
    opp_dto.title = "Title"
    opp_dto.agency = "Agency name"
    opp_dto.posted_date = "01/01/1999"
    opp_dto.type = "Solicitation"
    opp_dto.set_aside = "SBA"
    opp_dto.due_date = "02/01/1999"
    opp_dto.naics = "541519"
    opp_dto.url = "https://example.com"
    api_response.value = [opp_dto]

    mocker.patch("client.SamApi.search", return_value=api_response)
    assert api_response.to_dict()["value"] == sam.search(
        api_client, "abcd", "01/01/1999", "01/02/1999", 1000, "541519"
    )
