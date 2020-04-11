from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os

currentTime = datetime.datetime.now()


def barts(request):

    sites = {'Royal London Hospital': 'pr234ted',
             'Whipps Cross Hospital': 'el324os',
             'Barts': 'ak907atp',
             'Mile End Hospital': 'ap193fw',
             'Newham Hospital': 'th738go'}

    post = False
    site = None
    landing = request.args.get('landing')
    name = request.args.get('site')
    code = request.args.get('code')
    client = datastore.Client()
    print(f'landing:{landing};name:{name};code:{code}')

    if name and code:
        site = get_site(name, code, client)
    if site and request.method == 'POST':
        print ("data are being updated.")
        update_site(site, client, request, code)
        publish_update(site)
        post = True

    if landing == 'true':
        print('Landing == true')
        template = 'barts.html'

    else:
        print('Landing != true')
        site = get_site(name, code, client)
        template = 'success.html' if post else 'form.html' if site else 'error.html'

    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain = os.getenv('DOMAIN')
    form_action = f'https://{domain}/barts?site={name}&code={code}'
    landing_page = f'https://{domain}/barts?landing=true'

    print(f"Rendering {template}")

    response = make_response(render_template(template,
                                             site=site,
                                             sites=sites,
                                             form_action=form_action,
                                             landingPage=landing_page,
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))

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
    print(f"Updating site: {site}/{code}")
    # Update the site
    site.update(request.form)

    # Values not to change
    site['site'] = site.key.name
    site['acute'] = acute
    site['code'] = code

    print(f"Updating site {site}")
    client.put(site)


def publish_update(site):
    # Publish a message to update the Google Sheet:

    message = {}
    message.update(site)
    message['last_update'] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:%M %d %B %y')

    publisher = pubsub_v1.PublisherClient()

    project_id = os.getenv("PROJECT_ID")
    topic_path = publisher.topic_path(project_id, 'form-submissions')

    data = json.dumps(message).encode("utf-8")

    future = publisher.publish(topic_path, data=data)

    print(f"Published update to site {site.key.name}: {future.result()}")
