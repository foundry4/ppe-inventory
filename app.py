from flask import Flask, request
from barts.main import barts
from register.main import register
from form.main import form

import os

app = Flask(__name__)

@app.route('/barts')
def run_dashboard():
    app.template_folder = 'barts/templates'
    set_env()
    return barts(request)


@app.route('/register')
def run_register():
    set_env()
    return register(request)

@app.route('/form')
def run_form():
    app.template_folder = 'form/templates'
    set_env()
    return form(request)


def set_env():
    os.environ["DOMAIN"] = "127.0.0.1: 5000"
    os.environ["sheet_id"] = "1BhvOQnKWA7lKnH1dMKriiA2lZrk37mtyeALTG3ToEng"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\temp\\ppe-inventory-dev-66c9ad56f441.json"