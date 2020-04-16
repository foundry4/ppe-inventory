#
# This script is intended to run once to add new providers to the datastore from a csv file.
# It will also generate a list of [registration] links for the new providers and
# a list of duplicates providers if any are found with an identical name already in the input file.
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#           $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#
# Pass the PRODUCTION, TEST or DEV base url as a commandline argument as required e.g.
#
#           $ python3 load-providers.py https://********************.cloudfunctions.net
#

from google.cloud import datastore
import csv
import uuid
import sys

baseUrl = ''
if len(sys.argv) > 1:
    baseUrl = sys.argv[1]
else:
    print('No link base url was provided so no action taken')
    sys.exit(1)

print(f'Link base url is {baseUrl}')

# Read input from csv file
print('Reading records from input csv file...')

provider_dictionary = {}
duplicate_providers_list = []

with open('providers.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        provider = row[1].strip()
        email = row[10]
        address = row[12]
        code = str(uuid.uuid4())
        name = provider
        link = baseUrl + '/register?site=' + name + '&code=' + code

        if name in provider_dictionary.keys():
            duplicate_providers_list.append(
                {"code": provider_dictionary[name]['code'], "provider": provider_dictionary[name]['provider'],
                 "email": provider_dictionary[name]['email'], "address": provider_dictionary[name]['address']})
        provider_dictionary[name] = {
            "provider": provider,
            "code": code,
            "email": email,
            "address": address,
            "link": link
        }

# Write duplicates to file
print('Writing duplicate records to file duplicates.csv...')
f = open("duplicates.csv", "w")
for duplicate in duplicate_providers_list:
    f.write(
        duplicate.get('code') + ',' + duplicate.get('provider') + ',' + duplicate.get('email') + ',' + duplicate.get(
            'address') + '\n')
f.close()


print('Writing links to links.csv file and updating datastore...')

# Open file to write links to
f = open("links.csv", "w")

# Identify the 'kind' of entity
kind = 'Site'

# Instantiates a client
datastore_client = datastore.Client()

for key, value in provider_dictionary.items():
    provider = value.get('provider')
    code = value.get('code')
    email = provider_dictionary[key]['email']
    address = provider_dictionary[key]['address']

    # The Cloud Datastore key for the new entity
    task_key = datastore_client.key(kind, key)

    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task['provider'] = value.get('provider')
    task['code'] = value.get('code')
    task['email'] = value.get('email')
    task['address'] = value.get('address')

    # Saves the entity
    datastore_client.put(task)

    f.write(value.get('provider') + ',' + value.get('email') + ',' + value.get('link') + '\n')

f.close()
