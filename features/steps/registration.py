from behave import *


@given(u'I have a valid registration link')
def step_impl(context):
    context.link = context.valid_link


@given(u'I have an invalid registration link')
def step_impl(context):
    context.link = context.invalid_link


@when("I visit the link")
def step_impl(context):
    context.browser.get(context.link)


@then("I can see the form page")
def step_impl(context):
    assert context.browser.current_url == context.base_url + "/form"


@step("I see the provider's stock form")
def step_impl(context):
    assert context.browser.title == context.valid_provider_name + " - PPE Stock"


@step("I see that I am denied access")
def step_impl(context):
    assert 'You may need permission to access this service' in context.browser.page_source
