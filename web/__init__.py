from flask import Flask, current_app
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import json
import os
import threading
from .wiki import wiki
from .upload import upload
from .github import pull

app = Flask(__name__)
app.register_blueprint(wiki)
app.register_blueprint(upload)


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

# Clone wiki content
#pull()

# Run the app (if this file is called directly and not through 'flask run')
# This is isn't recommended, but it's good enough to run a low-traffic wiki
if __name__ == '__main__':
    app.run(host='0.0.0.0')