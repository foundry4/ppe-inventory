from selenium import webdriver
import os
import logging

logging.basicConfig(level=logging.INFO, filename="tests.log")


def before_all(context):
    context.portal_base_url = "https://" + os.getenv('PORTAL')
    context.base_url = "https://" + os.getenv('DOMAIN')
    context.valid_provider_name = os.getenv('VALID_PROVIDER_NAME')
    context.valid_provider_code = os.getenv('VALID_PROVIDER_CODE')
    context.invalid_provider_code = '99999'
    context.valid_link = context.base_url + "/register?site=" + str(
        context.valid_provider_name) + "&code=" + str(context.valid_provider_code)
    context.invalid_link = context.base_url + "/register?site=" + str(
        context.valid_provider_name) + f'&code={context.invalid_provider_code}'
    context.browser = webdriver.Chrome()


def after_all(context):
    context.browser.quit()
