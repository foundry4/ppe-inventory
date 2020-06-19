#
# This script is intended to add new providers and update existing providers in the datastore from an Excel input file.
#
# Pass the PROD, TEST or DEV base url as the first commandline argument and the input file as the second
# argument. A third argument identifying the out put file is optional. If this is not provided then the output file
# will tbe the timestamp appended with 'new-providers.xlsx'. For example:
#
#   $ python3 new-providers.py https://********.cloudfunctions.net "input-file.xlsx" "output-file.xlsx"
#
# An attempt is made to create a new record for each of the entries in the input file.
# If the provider already exists then the record is updated with the values from the input file
# but the code value is not changed so that the provider's link remains valid. In all cases the results
# and the links for the providers are appended to the output Excel file.
#
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#   $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#


from google.cloud import datastore
import uuid
import sys
import logging
import pandas as pd
import urllib.parse
from email_validator import validate_email, EmailNotValidError
import datetime
import csv
import urllib.parse

# Parameters
baseUrl = ''
if len(sys.argv) > 2:
    baseUrl = sys.argv[1]
    input_file = sys.argv[2]
else:
    print('Missing arguments i.e. first is the base url for the target environment and second is the input file.')
    sys.exit(1)

# Logging
now = datetime.datetime.now()
logfile = f'{now} new-providers.log'
logging.basicConfig(level=logging.INFO, filename=logfile)
print(f'Writing logs to "{logfile}" file ...')
logging.info(f'Base url is {baseUrl}')
logging.info(f'Input file is {input_file}')

# Datastore client
datastore_client = datastore.Client()

# Process CSV
with open(input_file, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:

        # Row values
        site = row.get('site')
        provider = row.get('provider')
        acute = row.get('acute')
        location = row.get('location')
        postcode = row.get('postcode')
        service_type = row.get('service_type')
        borough = row.get('borough')
        contact_name_1 = row.get('contact_name_1')
        contact_name_2 = row.get('contact_name_2')
        email_1 = row.get('email_1')
        email_2 = row.get('email_2')
        email_3 = row.get('email_3')
        telephone = row.get('telephone')
        pcn_network = row.get('pcn_network')
        practice_code = row.get('practice_code')
        parent = row.get('parent')
        parent_link = row.get('parent_link')

        # Check if record exists so can use existing code otherwise generate new code value
        provider_key = datastore_client.key('Site', site)
        existing_provider = datastore_client.get(provider_key)
        if existing_provider:
            comment = 'UPDATED'
            code = existing_provider['code']
            link = existing_provider['link']
            entity = existing_provider
        else:
            comment = 'CREATED'
            code = str(uuid.uuid4())
            link = 'https://' + baseUrl + '/register?site=' + urllib.parse.quote(site, safe='') + '&code=' + code
            entity = datastore.Entity(key=provider_key)

        # Update the entity values
        entity['code'] = code
        entity['site'] = site
        entity['provider'] = provider
        entity['acute'] = acute
        entity['location'] = location
        entity['postcode'] = postcode
        entity['service_type'] = service_type
        entity['borough'] = borough
        entity['contact_name_1'] = contact_name_1
        entity['contact_name_2'] = contact_name_2
        entity['email_1'] = email_1
        entity['email_2'] = email_2
        entity['email_3'] = email_3
        entity['telephone'] = telephone
        entity['pcn_network'] = pcn_network
        entity['practice_code'] = practice_code
        entity['parent'] = parent
        entity['parent_link'] = parent_link
        entity['link'] = link

        # Save the entity
        logging.info(entity)
        datastore_client.put(entity)

