# SAM.gov opportunity search and post to a chat channel
[![sam-search-build](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-build.yaml/badge.svg)](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-build.yaml) [![sam-search-run](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml/badge.svg)](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml)

Python client for the sam.gov opportunities API: https://open.gsa.gov/api/get-opportunities-public-api/. Searches by a list of NAICS codes and from-date, defaulting to a list of opps from the past day.

[sam-search-run](https://github.com/MindPetal/sam-search/actions/workflows/sam-search-run.yaml) pulls search results for specified NAICS each day and posts them to MS Teams, Slack, or both. Search config data is stored in [config.yaml](/config.yaml). To run this you must obtain and configure as actions repo secrets:

| Name | Value |
| ---- | ----- |
|`SAM_API_KEY`| SAM.gov API key for Contract Awards API access, created and tied to your SAM profile |
| `MS_URL`| MS Teams webhook URL. More info on setting up Teams webhooks: [Create incoming webhooks with Workflows for Microsoft Teams](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498)|
| `SLACK_URL`| Slack incoming webhook URL. Create a new app and webhook at [api.slack.com/apps](https://api.slack.com/apps).|

Set `MS_URL`, `SLACK_URL`, or both. Results are posted to every channel that has a URL, and the run fails at startup if neither is set.

> [!CAUTION]
> `SAM_API_KEY`, `MS_URL` and `SLACK_URL` are sensitive values. Store them only as GitHub Actions repository secrets. Never commit them, paste them into issues, pull requests, logs, etc. Secrets are not copied when the repo is forked or cloned. Each organization must create its own key and webhooks. If any of them is exposed, rotate it right away. Slack also detects and revokes webhook URLs that leak publicly.

> [!NOTE]
> The sam.gov get opportunities API does not allow searching by a list of NAICS like the front-end sam.gov web page does, so this client is making a series of GET requests for each NAICS configured in config.yaml. Sam.gov restricts non-federal accounts to 10 API requests per day, so this can only search a max of 10 NAICS per day. MS Teams and Slack also restrict the size of posted messages, so search results are broken into additional messages of 40 records each in Teams and 20 records each in Slack.

## Chat channels:
Posting is handled by one module per chat tool, called from `main` in [search.py](src/sam_search/search.py):
- [teams.py](src/sam_search/teams.py) builds MS Teams Adaptive Cards, splitting results into messages of 40 records.
- [slack.py](src/sam_search/slack.py) posts the same content as a Slack `table` block, splitting results into messages of 20 records each.

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
SLACK_URL='my-slack-webhook-url'
```
```sh
uv run --env-file .env sam-search
```
