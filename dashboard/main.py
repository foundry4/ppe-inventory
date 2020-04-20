from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
import datetime
import json
import os
import operator



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

    items =get_ppe_items (sites)
    items.append(get_ppe_item('Face visors', sites))
    ppe_item = {
                'name': 'Face visors',
                'under_one': '65%',
                'one_two': '20%',
                'two_three': '10%',
                'over_three': '5%',
                'highlight': True
                }
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


def get_ppe_item(name, sites):
    site_count = len(sites)
    ppe_item = {
        'name': name,
        'under_one': sum(1 for site in sites if site.RAG == 'one-or-less') / site_count,
        'one_two': sum(1 for site in sites if site.RAG == 'one_two') / site_count,
        'two_three': sum(1 for site in sites if site.RAG == 'two-three') / site_count,
        'over_three': sum(1 for site in sites if site.RAG == 'over_three') / site_count,
    }
    ppe_item['highlight'] = max(ppe_item.items(), key=operator.itemgetter(1))[0]


def get_ppe_items(sites):
    pass
