#
# This script is intended to create or update sites for the Barts Group and TEST.
#
# Pass the PROD, TEST or DEV base url as a commandline argument. For example:
#
#   $ python3 create-acute-and-test-sites.py https://********.cloudfunctions.net
#
# An attempt is made to create a new record for each of the entries in this file.
# If the provider already exists then the record is updated with the values from this file
# but the code value is not changed so that the provider's link remains valid.
#
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#   $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#

from google.cloud import datastore
import uuid
import sys

baseUrl = ''
if len(sys.argv) > 1:
    baseUrl = sys.argv[1]
else:
    print('Missing arguments i.e. the base url for the target environment is required.')
    sys.exit(1)

print('Creating Barts Health sites and TEST site')


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
    print(f'Processing provider data: {provider_data}')
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


# TEST site with code 12345
create_site(get_test_site())

# The Barts Group
create_site(get_acute_site('East London NHS Foundation Trust', 'Barts Health'))
create_site(get_acute_site('Homerton', 'Barts Health'))
create_site(get_acute_site('Mile End Hospital', 'Barts Health'))
create_site(get_acute_site('NEL Emergency Store', 'Barts Health'))
create_site(get_acute_site('NELFT', 'Barts Health'))
create_site(get_acute_site('Newham Hospital', 'Barts Health'))
create_site(get_acute_site('Nightingale Hospital', 'Barts Health'))
create_site(get_acute_site('Queens', 'Barts Health'))
create_site(get_acute_site('Queens and King George', 'Barts Health'))
create_site(get_acute_site('Royal London Hospital', 'Barts Health'))
create_site(get_acute_site('St Bartholomew', 'Barts Health'))
create_site(get_acute_site('Whipps Cross Hospital', 'Barts Health'))
