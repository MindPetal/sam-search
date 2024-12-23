# SAM.gov opportunity search and post to MS Teams
[![sam-search-build](https://github.com/MindPetalSoftwareSolutions/sam-search/actions/workflows/sam-search-build.yaml/badge.svg)](https://github.com/MindPetalSoftwareSolutions/sam-search/actions/workflows/sam-search-build.yaml)

Simple Python client for the sam.gov opportunities API: https://open.gsa.gov/api/get-opportunities-public-api/. Right now it just supports searching by a list of NAICS codes and from-date, defaulting to a list of opps from the past day. Additional search params are available via the sam.gov API for future usage.

An Actions workflow pulls search results for specified NAICS each day and posts to a designated MS Teams channel. Config data is stored in config.yaml. Users are responsible for obtaining and configuring as actions repo secrets:
- SAM_API_KEY: API key from sam.gov, which is tied to a personal account, and expires every 90 days.
- MS_URL: MS Teams webhook URL for your organization.

More info on setting up Teams webhooks and formatting messages:
- https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
- https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using

Unfortunately the sam.gov API does not right now allow searching by a list of NAICS like the front-end sam.gov web page does, so this client is making a series of GET requests for each NAICS configured in config.yaml. MS Teams also restricts the size of posted messages, so search results with over 40 records will be broken into additional Teams messages.

## Instructions for local execution:

- Python 3.13+ required.
- Install:

```sh
pip3 install . --use-pep517
```

- Tests:

```sh
pytest test_search.py
```

- Execute: pass sam api key, ms teams webhook url:

```sh
python3 search.py <sam api key> <webhook url>
```
