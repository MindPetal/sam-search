# SAM.gov opportunity search and post to a chat channel
[![sam-search-build](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-build.yaml/badge.svg)](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-build.yaml) [![sam-search-run](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml/badge.svg)](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml)

Python client for the sam.gov opportunities API: https://open.gsa.gov/api/get-opportunities-public-api/. Searches by a list of NAICS codes and from-date, defaulting to a list of opps from the past day.

[sam-search-run](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml) pulls search results for specified NAICS each day and posts them to a designated chat channel. MS Teams is currently the only implemented channel. Search config data is stored in [config.yaml](/config.yaml). To run this you must obtain and configure as actions repo secrets:

| Name | Value |
| ---- | ----- |
|`SAM_API_KEY`| SAM.gov API key for Contract Awards API access, created and tied to your SAM profile |
| `MS_URL`| Webhook URL for the chat channel to post to. Currently an MS Teams webhook. More info on setting up Teams webhooks: [Create incoming webhooks with Workflows for Microsoft Teams](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498)|

> [!CAUTION]
> `SAM_API_KEY` and `MS_URL` are sensitive values. Store them only as GitHub Actions repository secrets. Never commit them, paste them into issues, pull requests, logs, etc. Secrets are not copied when the repo is forked or cloned. Each organization must create its own key and webhook. If either one is exposed, rotate it right away.

> [!NOTE]
> The sam.gov get opportunities API does not allow searching by a list of NAICS like the front-end sam.gov web page does, so this client is making a series of GET requests for each NAICS configured in config.yaml. Sam.gov restricts non-federal accounts to 10 API requests per day, so this can only search a max of 10 NAICS per day. MS Teams also restricts the size of posted messages, so search results with over 40 records will be broken into additional Teams messages.

## Chat channels:
Posting is handled by one module per chat tool. [teams.py](src/sam_search/teams.py) builds MS Teams Adaptive Cards, splitting results into messages of 40 records, and posts them to the webhook. To support another tool, such as Slack, add a sibling module that provides the same two functions, and call it from `main` in [search.py](src/sam_search/search.py).

## Local execution:

Python 3.13+ required. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (`brew install uv`) and sync dependencies:
```sh
uv sync --dev
```

Lint:
```sh
uv run ruff check .
uv run ruff format --check .
```

Git hook (auto-formats Python files on commit):
```sh
git config core.hooksPath hooks
```

Type check:
```sh
uv run ty check
```

Tests:
```sh
uv run pytest
```

Execute (put the secrets in a gitignored `.env` file so they stay out of your shell history):
```sh
# .env
SAM_API_KEY='my-sam-api-key'
MS_URL='my-ms-webhook-url'
```
```sh
uv run --env-file .env sam-search
```
