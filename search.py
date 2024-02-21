"""
    Script executes via github actions to call 
    sam.gov opportunities API and post results to MS Teams. 
"""
from __future__ import print_function
from datetime import date, datetime, timedelta, timezone

import json
import logging
import sys

import certifi
import urllib3
import yaml
import client
from client.rest import ApiException

log = logging.getLogger('search')
logging.basicConfig(level=logging.INFO)

def load_config():
    # Load yaml config file
    with open(f'config.yaml', 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def search(api_client, api_key, from_date,
           to_date, limit, naics):
    # Execute sam.gov search
    api_instance = client.SamApi(api_client)

    try:
        api_response = api_instance.search(api_key=api_key, 
                                           posted_from=from_date,
                                           posted_to=to_date,
                                           limit=limit,
                                           naics=naics)
    except ApiException as e:
        log.exception("Exception when calling SamApi->search: %s\n" % e)
    
    return api_response.to_dict()['value']

def format_date(raw_date):
    # Format date/times to nice format
    formatted_date = None

    if bool(raw_date):

        if 'T' in raw_date:
            date_obj = datetime.fromisoformat(raw_date).astimezone()
            formatted_date = date_obj.strftime('%m/%d/%Y - %I:%M%p %Z')
        else:
            formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%m/%d/%Y')

    return formatted_date

def format_results(raw_results, naics_list):
    # Format a results string
    result_string = date.today().strftime(("%A, %m/%d/%Y"))
    result_string = result_string + f'\nTotal records: {len(raw_results)}'
    n = 1
    
    for result in raw_results:
        result_string = result_string + '\n\n------------------------------------------------------------------------'
        result_string = result_string + f'\n**{n}.**'
        result_string = result_string + f'\n**Title:     {result["title"]}**'
        result_string = result_string + f'\nAgency:    {result["agency"]}'
        result_string = result_string + f'\nPosted:    {format_date(result["posted_date"])}'
        result_string = result_string + f'\nDue:       {format_date(result["due_date"])}'
        result_string = result_string + f'\nType:      {result["type"]}'
        result_string = result_string + f'\nSet Aside: {result["set_aside"]}'

        naics_desc = next((naics for naics in naics_list 
                           if str(naics['code']) == result['naics']), None)['desc']
        
        result_string = result_string + f'\nNAICS:     {result["naics"]} - {naics_desc}'
        result_string = result_string + f'\nURL:       {result["url"]}'

        n += 1

    result_string = result_string + '\n\n\n\n'
    
    return result_string

def process_search(api_client, sam_api_key, from_days_back, naics_list):
    # Prepare sam.gov search and format results
    raw_results = []

    limit = 1000
    from_date = (date.today() - timedelta(days=from_days_back)).strftime("%m/%d/%Y")
    to_date = date.today().strftime("%m/%d/%Y")

    for naics in naics_list:
        naics_result = search(api_client, sam_api_key, from_date,
                              to_date, limit, naics['code'])
        
        for result in naics_result:
            raw_results.append(result)

    return format_results(raw_results, naics_list)

def ms_authn(api_client, body):
    # Execute MS authn
    api_instance = client.MsApi(api_client)

    try:
        api_response = api_instance.authn_post(body=body)

    except ApiException as e:
        log.exception("Exception when calling MsApi->authn: %s\n" % e)
    
    return api_response.to_dict()['access_token']

def process_ms_authn(api_client, tenant, id, secret):
    # Prepare MS authn post
    scope = 'https://graph.microsoft.com/.default'
    grant_type = 'client_credentials'
    body = f'client_id={id}&scope={scope}&client_secret={secret}&grant_type={grant_type}'
    
    return ms_authn(api_client, body)

def teams_post(api_client, content):
    # Execute MS Teams post
    api_instance = client.MsApi(api_client)

    try:
        api_response = api_instance.teams_post(body={'body':{'content': content}})

    except ApiException as e:
        log.exception("Exception when calling MsApi->teams_post: %s\n" % e)

def main(sam_api_key, ms_tenant, ms_app_id, ms_client_secret, 
         ms_team_id, ms_channel_id):
    # Primary processing fuction

    log.info('Start processing, load config data') 
    config = load_config()
    api_config = client.Configuration()
    api_config.host = config['sam_url']
    api_client = client.ApiClient(api_config)

    log.info('Process search')
    search_results = process_search(api_client, sam_api_key, 
                                    config['from_days_back'], config['naics'])
    
    log.info('Teams authn')
    api_config.host = config['ms_authn_url'].replace('tenant', ms_tenant)
    api_config.access_token = process_ms_authn(api_client, ms_tenant, 
                                               ms_app_id, ms_client_secret)
    log.info('Retrieved access token')

    log.info('Process Teams post')
    api_config.host = config['ms_channel_url'].replace('team-id', ms_team_id).replace('channel_id', ms_channel_id)
    teams_post(api_client, search_results)


""" Read in sam_api_key, ms_tenant, ms_app_id, ms_client_secret, ms_team_id, 
    ms_channel_id for script execution.
"""
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], 
         sys.argv[4], sys.argv[5], sys.argv[6])