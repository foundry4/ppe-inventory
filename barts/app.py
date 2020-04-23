from flask import Flask, request
import main as main
import os

app = Flask(__name__)

@app.route('/barts')
def run_barts():
    os.environ["DOMAIN"] = "127.0.0.1:5000"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\temp\\ppe-inventory-dev-66c9ad56f441.json"
    return main.barts(request)


if __name__ == "__main__":
    app.run(ssl_context='adhoc')