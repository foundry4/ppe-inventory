from behave import *
import time
import logging
from google.cloud import datastore


@given("that the new provider does not exist")
def step_impl(context):
    print(u'STEP: Given that the new provider does not exist')
    context.new_provider = f'New provider {int(time.time()*1000)} ms'
    logging.info(context.new_provider)


@when("I attempt to add the new provider")
def step_impl(context):
    print(u'STEP: When I attempt to add the new provider')
    # Instantiates a client
    datastore_client = datastore.Client()
    provider_key = datastore_client.key('Site', context.new_provider)
    entity = datastore.Entity(key=provider_key)
    entity['provider'] = context.new_provider
    datastore_client.put(entity)


@then("I am informed that the new provider record was created")
def step_impl(context):
    print(u'STEP: Then I am informed that the new provider record was created')


@step("the link for the provider is returned")
def step_impl(context):
    print(u'STEP: And the link for the provider is returned')


@given("that the new provider does exist")
def step_impl(context):
    print(u'STEP: Given that the new provider does exist')


@then("I am informed that the provider existed")
def step_impl(context):
    print(u'STEP: Then I am informed that the provider existed')