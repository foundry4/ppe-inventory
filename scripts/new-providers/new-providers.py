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

baseUrl = ''
if len(sys.argv) > 2:
    baseUrl = sys.argv[1]
    input_file = sys.argv[2]
else:
    print('Missing arguments i.e. first is the base url for the target environment and second is the input file.')
    sys.exit(1)
now = datetime.datetime.now()
logfile = f'{now} new-providers.log'
logging.basicConfig(level=logging.INFO, filename=logfile)
print(f'Writing logs to "{logfile}" file ...')
logging.info(f'Base url is {baseUrl}')
logging.info(f'Input file is {input_file}')
if len(sys.argv) > 3:
    output_file = sys.argv[3]
else:
    output_file = f'{now} new-providers.xlsx'
sheet_in = pd.read_excel(input_file)
sheet_out = pd.ExcelWriter(output_file)

df = pd.DataFrame(
    columns=['provider', 'code', 'link', 'site', 'acute', 'location', 'postcode', 'service_type', 'borough',
             'contact_name_1', 'contact_name_2', 'email_1', 'email_2', 'email_3', 'telephone',
             'pcn_network', 'practice_code', 'parent', 'parent_link', 'comment'])

logging.info(sheet_in.head)
logging.info(sheet_in.columns.ravel())

# Instantiates a client
datastore_client = datastore.Client()


# Helper functions to clean up input values
def get_clean_value(value):
    output = ''
    if pd.notnull(value):
        output = str(value).strip()
    return output


def get_provider(practice_name, postcode_input):
    provider_output = ''
    if pd.notnull(practice_name):
        provider_output = practice_name.strip()
    if pd.notnull(postcode_input):
        provider_output = str(provider_output + ' ' + postcode_input).strip()
    return provider_output


def get_site(practice_name, postcode_input):
    return get_provider(practice_name, postcode_input).replace("&", "and").strip()


def get_location(line1, line2, line3):
    location_str = ''
    if pd.notnull(line1):
        location_str = line1
    if pd.notnull(line2):
        location_str = location_str + ', ' + line2
    if pd.notnull(line3):
        location_str = location_str + ', ' + line3
    return location_str.strip()


def get_borough(ccg_input):
    borough_output = ''
    if pd.notnull(ccg_input):
        borough_output = str(ccg_input).strip()[4:-4]
    return borough_output


def get_email(email_input):
    email = ''
    if pd.notnull(email_input):
        email = email_input.replace(";", " ").replace("'", " ").replace("\n", " ").strip().split(' ', 1)[0]
        try:
            v = validate_email(email)
            email = v["email"].lower()
        except EmailNotValidError as e:
            logging.error(f'{str(e)}  [{email}] from [{email_input}]')
    return email


# Iterate over input file to calculate new values
for index, row in sheet_in.iterrows():
    provider = get_provider(row['Practice_Name'], row['Post_Code'])
    site = get_site(row['Practice_Name'], row['Post_Code'])
    acute = "no"
    location = get_location(row['Address_Line_1'], row['Address_Line_2'], row['Address_Line_3'])
    postcode = get_clean_value(row['Post_Code']).upper()
    service_type = "Primary Care - GP Federation"
    borough = get_borough(row['CCG'])
    contact_name_1 = get_clean_value(row['Practice_Manager_Name'])
    contact_name_2 = get_clean_value(row['Lead_GP_Name/GP Principals'])
    email_1 = get_email(row['Practice_Manager_email'])
    email_2 = get_email(row['Lead_GP_email'])
    email_3 = get_email(row['Alternative_Practice_Email address'])
    telephone = get_clean_value(row['Practice_Phone_Number_\n(Bypass)'])
    pcn_network = get_clean_value(row['PCN Network'])
    practice_code = get_clean_value(row['Practice Code'])
    parent = ""
    if parent != "":
        parent_link = 'https://' + baseUrl + '/children?parent=' + urllib.parse.quote(str(parent))
    else:
        parent_link = ""

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
        link = 'https://' + baseUrl + '/register?site=' + site + '&code=' + code
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

    # Write values to output data frame
    new_row = {'provider': provider, 'code': code, 'link': link, 'site': site, 'acute': acute, 'location': location,
               'postcode': postcode, 'service_type': service_type, 'borough': borough, 'contact_name_1': contact_name_1,
               'contact_name_2': contact_name_2, 'email_1': email_1, 'email_2': email_2, 'email_3': email_3,
               'telephone': telephone, 'pcn_network': pcn_network,
               'practice_code': practice_code, 'parent': parent, 'parent_link': parent_link, 'comment': comment}
    df = df.append(new_row, ignore_index=True)

# Write data frame to output file
print(f'Saving output file to "{output_file}"...')
df.to_excel(sheet_out)
sheet_out.save()
