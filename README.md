# SAM.gov opportunity search and post to MS Teams
[![sam-search-build](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-build.yaml/badge.svg)](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-build.yaml) [![sam-search-run](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml/badge.svg)](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml)

Python client for the sam.gov opportunities API: https://open.gsa.gov/api/get-opportunities-public-api/. Searches by a list of NAICS codes and from-date, defaulting to a list of opps from the past day.

The [SAM-Search-Run](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml) workflow pulls search results for specified NAICS each day and posts to a designated MS Teams channel. Search config data is stored in [config.yaml](/config.yaml). To run this you must obtain and configure as actions repo secrets:
- SAM_API_KEY: API key from sam.gov, which is tied to a personal account, and expires every 90 days.
- MS_URL: MS Teams webhook URL for your organization.

More info on setting up Teams webhooks: [Create incoming webhooks with Workflows for Microsoft Teams](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498)

> [!NOTE]
> The sam.gov get opportunities API does not allow searching by a list of NAICS like the front-end sam.gov web page does, so this client is making a series of GET requests for each NAICS configured in config.yaml. Sam.gov restricts non-federal accounts to 10 API requests per day, so this can only search a max of 10 NAICS per day. MS Teams also restricts the size of posted messages, so search results with over 40 records will be broken into additional Teams messages.

## Local execution:

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
python3 search.py my-sam-api-key my-ms-webhook-url
```
