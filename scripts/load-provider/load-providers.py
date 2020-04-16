#
# This script is intended to run once to add new providers to the datastore from a csv file.
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#           $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#

from google.cloud import datastore
import urllib
import csv
import uuid
import pprint
import sys

baseUrl = 'https://europe-west2-ppe-inventory-273009.cloudfunctions.net'
if len(sys.argv) > 1:
    baseUrl = sys.argv[1]
    print(f'Link base url is {baseUrl}')

# Read input from csv file

provider_dictionary = {}
duplicate_providers_list = []

with open('providers.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        provider = row[1].strip()
        email = row[10]
        address = row[12]
        code = str(uuid.uuid4())
        name = urllib.parse.quote_plus(provider)
        link = baseUrl + '/register?name=' + name + '&code=' + code

        if name in provider_dictionary.keys():
            print(f'Duplicate found for code provider {provider}')
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
f = open("duplicates.csv", "w")
for duplicate in duplicate_providers_list:
    pprint.pprint(duplicate)
    f.write(
        duplicate.get('code') + ',' + duplicate.get('provider') + ',' + duplicate.get('email') + ',' + duplicate.get(
            'address') + '\n')
f.close()

# Write links to file
f = open("links.csv", "w")

# Write to datastore

# Identify the 'kind' of entity
kind = 'Site'

# Instantiates a client
datastore_client = datastore.Client()

for key, value in provider_dictionary.items():
    print(key)
    pprint.pprint(value)
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
