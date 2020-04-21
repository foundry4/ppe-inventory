from flask import Flask, request
import main
import os

app = Flask(__name__)


@app.route('/')
def wrapper():
    return main.hello(request)


@app.route('/dashboard')
def run_dashboard():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\temp\\ppe-inventory-dev-66c9ad56f441.json"
    return main.dashboard(request)