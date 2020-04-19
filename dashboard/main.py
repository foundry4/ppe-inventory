from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
import datetime
import json
import os

def dashboard(request):

    siteNames = {'Royal London Hospital': 'pr234ted',
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

    sites = [get_site(name, code, client) for name, code in siteNames.items()]
    print(type(sites))
    print(type(sites[0]))
    print(len(sites))

    template = 'dashboard.html'
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain = os.getenv('DOMAIN')
    form_action = f'https://{domain}/barts?site={name}&code={code}'
    landing_page = f'https://{domain}/barts?landing=true'

    print(f"Rendering {template}")

    items = []
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)
    ppe_item = {'name': 'Face visors', 'under_one': '65%', 'one_two': '20%', 'two_three': '10%', 'over_three': '5%'}
    items.append(ppe_item)

    response = make_response(render_template(template,
                                             items=items,
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
