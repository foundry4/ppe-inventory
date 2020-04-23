from flask import Flask, request
import main as main
import os

app = Flask(__name__)


@app.route('/')
def wrapper():
    return main.hello(request)


@app.route('/register')
def run_register():
    os.environ["DOMAIN"] = "127.0.0.1:5000"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\temp\\ppe-inventory-dev-66c9ad56f441.json"
    return main.register(request)