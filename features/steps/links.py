from behave import *
from google.cloud import datastore
import os
import uuid


@given('the expected community sites exist')
def step_impl(context):
    print(f'STEP: Given the expected community sites exist')
    create_site(context, site='Links Site One LS1 5TY', borough='Barking & Dagenham', pcn='West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Two LS2 12PL', borough='Barking & Dagenham', pcn='East Five',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Three LS3 4RT', borough='City and Hackney', pcn='West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Four LS4 5TY', borough='Test borough', pcn='West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Five LS5 12PL', borough='Barking & Dagenham', pcn='South Six',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Six LS6 4RT', borough='Barking & Dagenham', pcn='South Six',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Seven LS7 5TY', borough='Havering', pcn='West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Eight LS8 12PL', borough='Havering', pcn='East Five',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Nine LS9 4RT', borough='Havering', pcn='West Four',
                service_type='Primary Care - GP Federation')
    create_site(context, site='Links Site Ten LS10 4RT', borough='Barking & Dagenham', pcn='West Four',
                service_type='Some other service type')


@when('I search for sites matching "{borough}", "{pcn}" and "{service_type}"')
def step_impl(context, borough, pcn, service_type):
    print(f'STEP: When I search for sites matching {borough}, {pcn} and {service_type}')
    # Instantiates a client
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Site')
    query.add_filter('borough', '=', borough)
    query.add_filter('pcn', '=', pcn)
    query.add_filter('service_type', '=', service_type)
    # query.order = ['site']
    # query = datastore_client.query()
    results = list(query.fetch())
    print(results)
    for site in results:
        print(site['site'])


@then('I can see the Links Result page')
def step_impl(context):
    print(f'STEP: Then I can see the Links Result page')


@step('I am shown links for the matching "{sites}"')
def step_impl(context, sites):
    print(f'STEP: And I am shown links for the matching {sites}')


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
    site_entity['pcn'] = pcn
    site_entity['service_type'] = service_type
    datastore_client.put(site_entity)
    print(datastore_client.get(site_key))
