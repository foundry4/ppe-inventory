from behave import *
from google.cloud import datastore
import os
import uuid
import pandas as pd


@given('site "{site}" exists')
def step_impl(context, site):
    print(f'STEP: Given provider {site} exists')
    context.domain = os.getenv('DOMAIN')
    # Instantiates a client
    datastore_client = datastore.Client()
    context.site_one = site
    provider_key = datastore_client.key('Site', context.site_one)
    datastore_client.delete(provider_key)
    entity = datastore.Entity(key=provider_key)
    entity['site'] = context.site_one
    code = str(uuid.uuid4())
    entity['code'] = code
    context.site_one_link = 'https://' + context.domain + '/register?site=' + site + '&code=' + code
    entity['link'] = context.site_one_link
    datastore_client.put(entity)


@step('site "{site}" does not exist')
def step_impl(context, site):
    print(f'STEP: And site {site} does not exists')
    context.provider_two = site
    # Instantiates a client
    datastore_client = datastore.Client()
    datastore_client.delete(datastore_client.key('Site', site))


@step("both sites are included in the input file")
def step_impl(context):
    context.file = 'features/resources/input-file.xlsx'
    print(f'STEP: And both sites are included in the input file at {context.file}')


@when("the input file is processed")
def step_impl(context):
    print(u'STEP: When the input file is processed')
    context.output_file = 'features/resources/output-file.xlsx'
    command = f'python3 scripts/new-providers/new-providers.py {context.domain} {context.file} {context.output_file}'
    print(command)
    os.system(command)


@then('site "{site}" is updated with the original link')
def step_impl(context, site):
    print(f'STEP: And site {site} is updated with the original link')
    # Instantiates a client
    datastore_client = datastore.Client()
    key = datastore_client.key('Site', site)
    assert key is not None
    entity = datastore_client.get(key)
    assert entity['link'] == context.site_one_link
    print(entity)


@then('site "{site}" is created with a new link')
def step_impl(context, site):
    print(f'STEP: Then {site} is created')
    # Instantiates a client
    datastore_client = datastore.Client()
    key = datastore_client.key('Site', site)
    assert key is not None
    entity = datastore_client.get(key)
    assert entity['link'] == 'https://' + context.domain + '/register?site=' + site + '&code=' + entity['code']
    print(entity)


@step('site "{site}" appears in the output file as "{status}"')
def step_impl(context, site, status):
    print(f'STEP: And site {site} appears in the output file as {status}')
    df = pd.read_excel(context.output_file)
    row = df.loc[df['site'] == site]
    print(row)
    assert row['comment'].values[0] == status
