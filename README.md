# SAM.gov opportunity search and post to MS Teams
[![sam-search](https://github.com/MindPetalSoftwareSolutions/sam-search/actions/workflows/sam-search.yaml/badge.svg)](https://github.com/MindPetalSoftwareSolutions/sam-search/actions/workflows/sam-search.yaml)

Simple Python client for the sam.gov opportunities API: https://open.gsa.gov/api/get-opportunities-public-api/. Right now it just supports searching by a list of NAICS codes and from-date, defaulting to a list of opps from the past day. Additional search params are available via the sam.gov API for future usage.

An Actions workflow pulls search results for specified NAICS each day and posts to a designated MS Teams chat. Credentials/MS Teams URL are stored as GitHub repo secrets, config data is in config.yaml. API key must be requested via sam.gov, is tied to a personal account, and expires every 90 days. 

Unfortunately the sam API does not right now allow searching by a list of NAICS like the front-end web page does, so this client is making a series of GET requests for each NAICS configured in config.yaml.

## Instructions for local execution:

- Python 3.4+ required.
- Install:

```sh
pip3 install . --use-pep517
```

- Execute: pass sam api key, MS Teams URL:

```sh
python3 search.py <api key> <url>
```

E.g.:

```sh
python3 search.py 1234abcd https://
```