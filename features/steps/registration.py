from behave import *
import logging


@given(u'I have a valid registration link')
def step_impl(context):
    context.link = context.valid_link
    context.site_code = context.valid_provider_code


@given(u'I have an invalid registration link')
def step_impl(context):
    context.link = context.invalid_link
    context.site_code = context.invalid_provider_code


@when("I visit the link")
def step_impl(context):
    logging.info('STEP: I visit the link')
    logging.info(f'Link => {context.link}')
    context.browser.get(context.link)


@then("I can see the form page")
def step_impl(context):
    logging.info(f'context.portal_base_url = {context.portal_base_url}')
    logging.info(f'context.portal_base_url = {context.portal_base_url}')
    logging.info(f'context.site_code = {context.site_code}')
    assert context.browser.current_url == f'{context.portal_base_url}/sites/{context.site_code}'


@step("I see the provider's stock form")
def step_impl(context):
    assert context.browser.title == "PPE Inventory | Site Form"


@step("I see that I am denied access")
def step_impl(context):
    assert f'The site with code: {context.invalid_provider_code} cannot be found' in context.browser.page_source
