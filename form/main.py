from flask import request, make_response, redirect, render_template, abort
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os


def form(request):

    name = request.cookies.get('site')
    code = request.cookies.get('code')

    client = datastore.Client()

    site = None
    if name and code:
        site = get_site(name, code, client)

    if site and request.method == 'POST':
        update_site(site, client, request, code)
        publish_update(site)
 
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain=os.getenv('DOMAIN')
    form_action = f'https://{domain}/form'

    template = 'form.html' if site else 'error.html'
    print(f"Rendering {template}")

    response = make_response(render_template(template, 
        site=site,
        form_action=form_action,
        assets='https://storage.googleapis.com/ppe-inventory',
        data={}
        ))
    
    if site:
        # Refresh the cookie
        expire_date = datetime.datetime.now() + datetime.timedelta(days=90)
        response.set_cookie('site', site.key.name, expires=expire_date, secure=True, httponly=True)
        response.set_cookie('code', site['code'], expires=expire_date, secure=True, httponly=True)

    return response


def get_site(name, code, client):

    print(f"Getting site: {name}/{code}")
    key = client.key('Site', name)
    site = client.get(key)
    if site and site.get('code') == code:
        return site
    return None


def update_site(site, client, request, code):
    
    acute = site.get('acute')

    # Update the site
    site.update(request.form)

    # Values not to change
    site['site'] = site.key.name
    site['acute'] = acute
    site['code'] = code

    client.put(site)


def publish_update(site):

    # Publish a message to update the Google Sheet:

    message = {}
    message.update(site)
    message['last_update'] = (datetime.datetime.now()+ datetime.timedelta(hours=1)).strftime('%I:%M %d %B %y')

    publisher = pubsub_v1.PublisherClient()

    project_id = os.getenv("PROJECT_ID")
    topic_path = publisher.topic_path(project_id, 'form-submissions')

    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    print(f"Published: {future.result()}")
