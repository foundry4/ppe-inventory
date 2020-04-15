#
# This script is intended to run once to add new providers to the datastore from a csv file.
# The script will try to use the credentials of a locally configured service account so it
# is important to provide the key file as an environment variable e.g.
#
#           $ export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
#
from google.cloud import datastore
import csv
import uuid
# Instantiates a client
datastore_client = datastore.Client()

# The kind for the new entity
kind = 'Site'

with open('providers.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        provider = row[1]
        email = row[10]
        address = row[12]
        code = str(uuid.uuid4())
        print(f'provider => {provider}   uuid => {code}   email => {email}   address => {address}')

        # The name/ID for the new entity
        name = provider

        # The Cloud Datastore key for the new entity
        task_key = datastore_client.key(kind, name)

        # Prepares the new entity
        task = datastore.Entity(key=task_key)
        task['code'] = code
        task['email'] = email
        task['address'] = address

        # Saves the entity
        datastore_client.put(task)
