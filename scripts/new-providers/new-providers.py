#
# This script is intended to add new providers and update existing providers in the datastore from an Excel input file.
#
# Pass the PROD, TEST or DEV base url as the first commandline argument and the the input file as the second
# argument e.g.
#
#   $ python3 new-providers.py https://********.cloudfunctions.net "North East Primary Care Contact List v(8) (8).xlsx"
#
# An attempt is made to create a new record for each of the entries in the input file.
# If the provider already exists then the record is updated with the values from the input file
# but the code value is not changed so that the provider's link remains valid. In all cases the results
# and the links for the providers are appended to the output file.
#
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#   $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#


from google.cloud import datastore
import csv
import uuid
import sys
import logging
from notifications_python_client.notifications import NotificationsAPIClient
import os
import pandas as pd

baseUrl = ''
if len(sys.argv) > 2:
    baseUrl = sys.argv[1]
    input_file = sys.argv[2]
else:
    print('Two arguments are required i.e. the base url for the target environment and then the input file.')
    sys.exit(1)

logfile = "new-providers.log"
logging.basicConfig(level=logging.INFO, filename=logfile)

print(f'logging to {logfile} ...')
logging.info(f'Link base url is {baseUrl}')

# Read from input file
logging.info('Reading records from input file...')
input_spreadsheet = pd.read_excel(input_file)
print(input_spreadsheet.head)

print(input_spreadsheet.columns.ravel())

# Instantiates a client
datastore_client = datastore.Client()

f = open(input_file + "-output.csv", "w+")

ProviderObjects = {}

for index, row in input_spreadsheet.iterrows():

    provider = str(str(row['Practice_Name']) + " " + str(row['Post_Code'])).replace("&", "and").strip()  # Both required to produce unique key
    acute = "no"  # I think in this case
    organisation = ""
    location = str(str(row['Address_Line_1']) + " " + str(row['Address_Line_2']) + " " + str(row['Address_Line_3'])).strip()  # Could be improved
    postcode = str(row['Post_Code']).upper().strip()
    service_type = ""  # Not in the input file but was in the the first version of input file
    borough = ""  # Not in the input file but was in the the first version of input file
    contact_name_1 = str(row['Practice_Manager_Name']).strip()
    contact_name_2 = str(row['Lead_GP_Name/GP Principals']).strip()
    contact_name_3 = ""  # Not in the input file but they have provided 3 emails
    email_1 = str(row['Practice_Manager_email']).strip()
    email_2 = str(row['Lead_GP_email']).strip()
    email_3 = str(row['Alternative_Practice_Email address']).strip()
    telephone_1 = str(row['Practice_Phone_Number_\n(Bypass)']).strip()
    telephone_2 = str(row['Practice_Phone_Number_(Public)']).strip()
    telephone_3 = ""  # Not in the input file but they have provided 3 emails
    # Are these GP specific fields?
    ccg = str(row['CCG']).strip()
    ods_code = str(row['ODS Code']).strip()
    cont_type = str(row['Cont Type']).strip()
    pcn_network = str(row['PCN Network']).strip()
    practice_code = str(row['Practice Code']).strip()
    practice_type = str(row['Branch/\nGP Led/\nWalk in Centre']).strip()

    # Check if record exists so can use existing code otherwise generate new code value
    existing_provider = datastore_client.get(datastore_client.key('Site', provider))
    if existing_provider:
        comment = 'EXISTING'
        code = existing_provider['code']
    else:
        comment = 'NEW     '
        code = str(uuid.uuid4())

    # Prepare to create or update the entity
    provider_key = datastore_client.key('Site', provider)
    entity = datastore.Entity(key=provider_key)
    entity['code'] = code
    entity['provider'] = provider
    entity['acute'] = acute
    entity['organisation'] = organisation
    entity['location'] = location
    entity['postcode'] = postcode
    entity['service_type'] = service_type
    entity['borough'] = borough
    entity['contact_name_1'] = contact_name_1
    entity['contact_name_2'] = contact_name_2
    entity['contact_name_3'] = contact_name_3
    entity['email_1'] = email_1
    entity['email_2'] = email_2
    entity['email_3'] = email_3
    entity['telephone_1'] = telephone_1
    entity['telephone_2'] = telephone_2
    entity['telephone_3'] = telephone_3
    entity['ccg'] = ccg
    entity['ods_code'] = ods_code
    entity['cont_type'] = cont_type
    entity['pcn_network'] = pcn_network
    entity['practice_code'] = practice_code
    entity['practice_type'] = practice_type



    # Saves the entity
    datastore_client.put(entity)

    link = baseUrl + '/register?site=' + provider + '&code=' + code
    link = '{0: <200}'.format(link)
    line = f'{comment}, {link} \n'
    logging.info(line)
    f.write(line)

f.close()

notifications_client = NotificationsAPIClient(os.getenv('EMAIL_API_KEY'))

response = notifications_client.get_template(
    'a9b20e19-efe9-4e6a-b081-67b549e596dc'  # required string - template ID
)

print(response)

response = notifications_client.send_email_notification(
    email_address='frank@notbinary.co.uk',  # required string
    template_id='a9b20e19-efe9-4e6a-b081-67b549e596dc',  # required UUID string
)

print(response)


