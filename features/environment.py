from selenium import webdriver
from behave import *

use_step_matcher("re")


def before_all(context):
    context.domain = "https://europe-west2-ppe-inventory-dev.cloudfunctions.net"
    context.valid_link = context.domain + "/register?site=ABERFELDY PRACTICE&code=b3860187-d3d2-4b33-a047-9b8c3e5f4bcc"
    context.invalid_link = context.domain + "/register?site=ABERFELDY PRACTICE&code=b3860187"
    context.environment = 'dev'
    context.browser = webdriver.Chrome()


def after_feature(context, feature):
    context.browser.quit()
