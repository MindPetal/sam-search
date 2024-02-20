# SAM.gov opportunity search and post to MS Teams
[![sam-search](https://github.com/MindPetalSoftwareSolutions/sam-search/actions/workflows/sam-search.yaml/badge.svg)](https://github.com/MindPetalSoftwareSolutions/sam-search/actions/workflows/sam-search.yaml)

Simple Python client for the sam.gov opportunities API: https://open.gsa.gov/api/get-opportunities-public-api/. Right now it just supports searching by a list of NAICS codes and from-date, defaulting to a list of opps from the past day. Additional search params are available via the sam.gov API for future usage.

An Actions workflow pulls search results for specified NAICS each day and posts to a designated MS Teams chat. Config data is stored in config.yaml. Users are responsible for obtaining and configuring as repo secrets:
- Sam.gov API key from sam.gov, which is tied to a personal account, and expires every 90 days.
- MS tenant id for your organization
- MS client id for your application
- MS client secret for your application
- MS team id
- MS channel id

More info on obtaining the required MS values and registering applications:
- https://learn.microsoft.com/en-us/graph/auth-v2-service
- https://learn.microsoft.com/en-us/graph/auth-register-app-v2
- https://learn.microsoft.com/en-us/graph/api/chatmessage-post

Unfortunately the sam API does not right now allow searching by a list of NAICS like the front-end web page does, so this client is making a series of GET requests for each NAICS configured in config.yaml.

## Instructions for local execution:

- Python 3.9+ required.
- Install:

```sh
pip3 install . --use-pep517
```

- Execute: pass sam api key, ms tenant id, ms app id, ms client secret, ms team id, ms channel id:

```sh
python3 search.py <sam api key> <ms tenant id> <ms app id> <ms client secret> <ms team id> <ms channel id>
```
