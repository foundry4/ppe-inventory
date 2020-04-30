from google.cloud import datastore
import uuid
import sys
import os

baseUrl = ''
if len(sys.argv) > 1:
    baseUrl = sys.argv[1]
else:
    print('Missing arguments i.e. the base url for the target environment is required.')
    sys.exit(1)

print('Creating Acute and TEST users')


def get_test_site():
    provider_data = {
        'acute': 'yes',
        'provider': 'TEST',
        'parent': '',
        'borough': '',
        'pcn_network': '',
        'service_type': ''
    }
    return provider_data


def get_acute_site(provider, parent):
    provider_data = {
        'acute': 'yes',
        'provider': provider,
        'parent': parent,
        'borough': '',
        'pcn_network': '',
        'service_type': ''
    }
    return provider_data


def get_community_site(provider, parent, borough, pcn, service_type):
    provider_data = {
        'acute': 'no',
        'provider': provider,
        'parent': parent,
        'borough': borough,
        'pcn_network': pcn,
        'service_type': service_type
    }
    return provider_data


def create_site(provider_data):
    print(f'creating site: {provider_data}')
    # Instantiates a client
    datastore_client = datastore.Client()
    site = provider_data['provider'].replace("&", "and").strip()
    site_key = datastore_client.key('Site', site)
    site_entity = datastore_client.get(site_key)
    if not site_entity:
        print(f'Site {site} does not exist so create it...')
        site_entity = datastore.Entity(key=site_key)
        site_entity['site'] = site
        if site == 'TEST':
            code = '12345'
        else:
            code = str(uuid.uuid4())
        site_entity['code'] = code
        link = 'https://' + baseUrl + '/register?site=' + site + '&code=' + code
        site_entity['link'] = link
    else:
        print(f'Site {site} does exist so updating it...')
    site_entity['acute'] = provider_data['acute']
    site_entity['parent'] = provider_data['parent']
    site_entity['borough'] = provider_data['borough']
    site_entity['pcn_network'] = provider_data['pcn_network']
    site_entity['service_type'] = provider_data['service_type']
    datastore_client.put(site_entity)
    print(datastore_client.get(site_key))


create_site(get_test_site())

create_site(get_acute_site('Barts', 'Barts Group'))
create_site(get_acute_site('East London NHS Foundation Trust', 'Barts Group'))
create_site(get_acute_site('Homerton', 'Barts Group'))
create_site(get_acute_site('Mile End Hospital', 'Barts Group'))
create_site(get_acute_site('NEL Emergency Store', 'Barts Group'))
create_site(get_acute_site('NELFT', 'Barts Group'))
create_site(get_acute_site('Newham Hospital', 'Barts Group'))
create_site(get_acute_site('Nightingale Hospital', 'Barts Group'))
create_site(get_acute_site('Queens', 'Barts Group'))
create_site(get_acute_site('Queens and King George', 'Barts Group'))
create_site(get_acute_site('Royal London Hospital', 'Barts Group'))
create_site(get_acute_site('St Bartholomew', 'Barts Group'))
create_site(get_acute_site('Whipps Cross Hospital', 'Barts Group'))
