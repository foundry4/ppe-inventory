from selenium import webdriver
import os


def before_all(context):
    context.base_url = "https://" + os.getenv('DOMAIN')
    context.valid_provider_name = os.getenv('VALID_PROVIDER_NAME')
    context.valid_provider_code = os.getenv('VALID_PROVIDER_CODE')
    context.valid_link = context.base_url + "/register?site=" + str(context.valid_provider_name) + "&code=" + str(
        context.valid_provider_code)
    context.invalid_link = context.base_url + "/register?site=" + str(
        context.valid_provider_name) + "&code=99999999999999999999999999"
    context.browser = webdriver.Chrome()


def after_feature(context, feature):
    context.browser.quit()
