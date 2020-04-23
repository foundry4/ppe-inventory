from behave import *
from google.cloud import datastore
import os
import uuid


@given('provider "{provider}" exists')
def step_impl(context, provider):
    print(u'STEP: Given provider Provider One exists')
    context.provider_one = provider
    # Instantiates a client
    datastore_client = datastore.Client()
    provider_key = datastore_client.key('Site', context.provider_one)
    datastore_client.delete(provider_key)
    entity = datastore.Entity(key=provider_key)
    entity['provider'] = context.provider_one
    entity['code'] = str(uuid.uuid4())
    datastore_client.put(entity)


@step('provider "{provider}" does not exist')
def step_impl(context, provider):
    print(u'STEP: And provider Provider Two does not exists')
    context.provider_two = provider
    # Instantiates a client
    datastore_client = datastore.Client()
    datastore_client.delete(datastore_client.key('Site', provider))


@step("both providers are included in the input file")
def step_impl(context):
    print(u'STEP: And both providers are included in the input file')
    f = open("new-providers.csv", "w+")
    f.write('provider,borough,contact_name,contact_email,telephone,service_type,location,postcode\n')
    f.write(
        f'{context.provider_one},borough1,contact_name1,contact_email1,telephone1,service_type1,location1,postcode1\n')
    f.write(
        f'{context.provider_two},borough2,contact_name2,contact_email2,telephone2,service_type2,location2,postcode2\n')
    f.close()


@when("the input file is processed")
def step_impl(context):
    print(u'STEP: When the input file is processed')
    os.system('pwd')
    os.system(f'python3 scripts/new-providers/new-providers.py {os.getenv("DOMAIN")}')


@step('"{provider}" is updated with the original link')
def step_impl(context, provider):
    print(u'STEP: And Test Provider Two is updated')


@then('"{provider}" is created with a new link')
def step_impl(context, provider):
    print(f'STEP: Then {provider} is created')
    # Instantiates a client
    datastore_client = datastore.Client()
    key = datastore_client.key('Site', provider)
    p = datastore_client.get(key)
    print(p)
