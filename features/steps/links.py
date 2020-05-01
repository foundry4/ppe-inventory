from behave import *
from google.cloud import datastore
import os
import uuid
import time
import urllib


@given('the expected community sites exist')
def step_impl(context):
    print(f'STEP: Given the expected community sites exist')
    create_site(context, site='Site One LS1 5TY', borough='Barking & Dagenham', pcn='Test East',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Two LS2 12PL', borough='Barking & Dagenham', pcn='Test East',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Three LS3 4RT', borough='City and Hackney', pcn='West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Four LS4 5TY', borough='Barking & Dagenham', pcn='Test East',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Five LS5 12PL', borough='Newham', pcn='Test Central',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Six LS6 4RT', borough='Newham', pcn='Test Central',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Seven LS7 5TY', borough='Havering', pcn='Test West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Eight LS8 12PL', borough='Havering', pcn='East Five',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Nine LS9 4RT', borough='Havering', pcn='Test West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Site Ten LS10 4RT', borough='Barking & Dagenham', pcn='West Four',
                service_type='Some other service type')


@when('I search for sites matching "{borough}", "{pcn}" and "{service_type}"')
def step_impl(context, borough, pcn, service_type):
    print(f'STEP: When I search for sites matching {borough}, {pcn} and {service_type}')
    context.borough = borough
    context.pcn = pcn
    context.service_type = service_type
    # Instantiates a client
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Site')
    query.add_filter('borough', '=', borough)
    query.add_filter('pcn_network', '=', pcn)
    query.add_filter('service_type', '=', service_type)
    results = list(query.fetch())
    print(query)
    print(results)
    for site in results:
        print(site['site'])


@then('I can see the Links Result page')
def step_impl(context):
    print(f'STEP: Then I can see the Links Result page')
    safe_borough = urllib.parse.quote(context.borough)
    safe_pcn = urllib.parse.quote(context.pcn)
    safe_service_type = urllib.parse.quote(context.service_type)
    query_params = f'search_type=links&service_type={safe_service_type}&borough={safe_borough}&pcn={safe_pcn}'
    print(query_params)
    url = f'{context.base_url}/search?{query_params}'
    context.browser.get(url)
    print(url)


@step('I am shown links for the matching "{sites}"')
def step_impl(context, sites):
    print(f'STEP: And I am shown links for the matching {sites}')
    site_names = sites.split(',')
    for s in site_names:
        context.browser.find_element_by_name(s)
        print(s)
    time.sleep(2)


def create_site(context, site, borough, pcn, service_type):
    context.domain = os.getenv('DOMAIN')
    # Instantiates a client
    datastore_client = datastore.Client()
    site_key = datastore_client.key('Site', site)
    site_entity = datastore_client.get(site_key)
    if not site_entity:
        print(f'Site {site} does not exist so create it...')
        site_entity = datastore.Entity(key=site_key)
        site_entity['site'] = site
        code = str(uuid.uuid4())
        site_entity['code'] = code
        link = 'https://' + context.domain + '/register?site=' + site + '&code=' + code
        site_entity['link'] = link
    site_entity['borough'] = borough
    site_entity['pcn_network'] = pcn
    site_entity['service_type'] = service_type
    datastore_client.put(site_entity)
    print(datastore_client.get(site_key))
