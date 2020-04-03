from flask import Flask, current_app, request, make_response, redirect, render_template, send_from_directory, abort
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import json
import os
import requests


def ppe_inventory_form(request):

    site = request.cookies.get('site')
    if not site:
        abort(400)

    url = "https://europe-west2-ppe-inventory.cloudfunctions.net/inventory"

    response = requests.get(url,
                            params={'site': site})
    if response.status_code != 200:
        print(response)
        raise Exception(f"Error: {response.status_code}")

    form = make_response(render_template('ppe-inventory.html', 
        data=response.json()
        ))
    form.set_cookie('hospital', hospital)
    return form

@app.route('/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Fix for Govuk frontend requests. """
    print(f"Fixed govuk path: /assets/{path}")
    return send_from_directory('static/assets', path)


# Run the app (if this file is called directly and not through 'flask run')
# This is isn't recommended, but it's good enough to run a low-traffic wiki
print("Startup...")
if __name__ == '__main__':
    print("Let's go!")
    port = os.getenv('PORT') or 5000
    app.run(host='0.0.0.0', port=port)
else:
    print(f"Name is {__name__}")