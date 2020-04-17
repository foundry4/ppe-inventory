from behave import *

use_step_matcher("re")


@given("I have a valid registration link")
def step_impl(context):
    context.registration_link = 'gfsfdggdgd'


@when("I visit the registration page with a valid link")
def step_impl(context):
    context.browser.get(context.valid_link)
    context.browser.save_screenshot('features/screenshots/I visit the registration page with a valid link.png')


@then("I can see the Form page")
def step_impl(context):
    assert context.browser.current_url == context.domain + "/form"


@step("I see the provider name")
def step_impl(context):
    assert 'ABERFELDY PRACTICE' in context.browser.page_source


@step("I see that I am denied access")
def step_impl(context):
    assert 'You may need permission to access this service' in context.browser.page_source


@when("I visit the registration page with an invalid link")
def step_impl(context):
    context.browser.get(context.invalid_link)
    context.browser.save_screenshot('features/screenshots/I visit the registration page with an invalid link.png')
