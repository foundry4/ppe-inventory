from flask import Flask, current_app, request, make_response, redirect, render_template, send_from_directory
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import json
import os
import threading

app = Flask(__name__)


# Redirect to https, but allow this to be disabled in development

if os.getenv('NOSSL'):
    print("Configured to not require SSL.")
else:
    print("Setting up redirect to SSL.")
    sslify = SSLify(app)


# Set up password protection

username = os.getenv('USERNAME', '')
password = os.getenv('PASSWORD', '')
if username and password:
    print(f"Setting up authentication for user {username}")
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app) 
else:
    print(f"Not setting up authentication. USERNAME: {username}, PASSWORD set: {password != ''}")


@app.route('/', methods=['GET'])
def redirect_to_form():
    return redirect("/ppe-inventory")

@app.route('/ppe-inventory', methods=['GET'])
def ppe_inventory_form():
    """ Form to upload images and other files to the wiki. """

    if 'hospital' in request.args:
        hospital = request.args.get('hospital')
    elif 'hospital' in request.cookies:
        hospital = request.cookies['hospital']

    response = make_response(render_template('ppe-inventory.html', 
        hospital=hospital
        ))
    response.set_cookie('hospital', hospital)
    return response

@app.route('/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Fix for Govuk frontend requests. """
    print(f"Fixed govuk path: /assets/{path}")
    return send_from_directory('static/assets', path)



# Run the app (if this file is called directly and not through 'flask run')
# This is isn't recommended, but it's good enough to run a low-traffic wiki
if __name__ == '__main__':
    port = os.getenv('PORT') or 5000
    app.run(host='0.0.0.0', port=port)