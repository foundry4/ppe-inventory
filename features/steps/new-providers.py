from behave import *


@given("that the new provider does not exist")
def step_impl(context):
    print(u'STEP: Given that the new provider does not exist')


@when("I attempt to add the new provider")
def step_impl(context):
    print(u'STEP: When I attempt to add the new provider')


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