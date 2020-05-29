from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os
import sys
import numpy as np

currentTime = datetime.datetime.now()


def form(request):
    landing = request.args.get('landing')
    name = request.args.get('site')
    code = request.args.get('code')
    parent = request.args.get('parent')

    client = datastore.Client()
    site = None
    post = False
    sites=[]
    landing_page = ''
    print(f'request method: {request.method}', file=sys.stderr)
    print(f'name:{name};code:{code}')
    print(f'parent:{parent}')
    if name and code:
        print(1)
        site = get_site(name, code, client)
        print(site.get('code'), file=sys.stderr)
    if site and request.method == 'POST':
        print(2)
        print("data are being updated.", file=sys.stderr)
        update_site(site, client, request, code)
        update_ppe_item(site, client)
        publish_update(get_sheet_data(site))
        post = True

    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain = os.getenv('DOMAIN')
    form_action = f'https://{domain}/form?site={name}&code={code}'
    dashboard_link = f'https://{domain}/dashboard'

    if post and parent:
        print(3)
        template = 'success.html'
        landing_page = f'https://{domain}/form?landing=true&code={code}'
    elif post:
        print(4)
        template = 'success.html'
    elif landing and code:
        print(5)
        template = 'landing.html'
        form_action = f'https://{domain}/form?landing=true&code={code}'
        sites = get_child_sites(code)
        parent=code
    elif site and 'acute' in site.keys() and site['acute'] == 'yes':
        print(6)
        template = 'form.html'
    elif site:
        print(7)
        template = 'community_form.html'
    else:
        print(8)
        template = 'error.html'

    # template = 'success.html' if post else 'form.html' if site else 'error.html'
    print(f"Rendering {template}")

    response = make_response(render_template(template,
                                             site=site,
                                             sites=sites,
                                             form_action=form_action,
                                             landingPage=landing_page,
                                             parent=parent,
                                             dashboard_link=dashboard_link,
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))

    if site:
        print(9, file=sys.stderr)
        # Refresh the cookie
        expire_date = datetime.datetime.now() + datetime.timedelta(days=90)
        response.set_cookie('site', site.key.name, expires=expire_date, secure=True)
        response.set_cookie('code', site['code'], expires=expire_date, secure=True)

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

    site["last_update"] = datetime.datetime.now()

    # Values not to change
    site['site'] = site.key.name
    site['acute'] = acute
    site['code'] = code
    site['updated'] = datetime.datetime.now()

    print(f"Updating site {site}")
    client.put(site)


def update_ppe_item(site, client):
    acute = site.get('acute')
    if acute != 'yes':
        item_names = 'face-visors', \
                     'goggles', \
                     'masks-iir', \
                     'masks-ffp2', \
                     'masks-ffp3', \
                     'gloves', \
                     'gowns', \
                     'hand-hygiene', \
                     'apron'

        # Instantiates a client
        query = client.query(kind='Ppe-Item')
        query.add_filter('provider', '=', site.get('site'))
        items = list(query.fetch())
        print(f"found {len(items)} for site {site.get('site')}")

        for item_name in item_names:
            stock_items = [item for item in items if item.get('item_name') == item_name]
            print(f"found {len(stock_items)} for site {site.get('site')} and item {item_name}")
            if len(stock_items) == 0:
                item_entity = datastore.Entity(client.key('Ppe-Item'))

            else:
                item_entity = stock_items[0]
            stock_level = int(site.get(item_name + '-stock-levels')) if site.get(item_name + '-stock-levels') else 0
            quantity_used = int(site.get(item_name + '-quantity_used')) if site.get(item_name + '-quantity_used') else 0
            daily_usage = float('nan') if quantity_used == 0 and stock_level != 0 \
                else 0 if stock_level == 0 \
                else stock_level / quantity_used
            rag = 'under_one' if daily_usage < 1 else \
                'one_two' if daily_usage < 2 else \
                'two_three' if daily_usage < 3 else \
                'less-than-week' if daily_usage < 7 else \
                'more-than-week' if daily_usage >= 7 else ''

            item_entity['provider'] = site.get('site')
            item_entity['item_name'] = item_name
            item_entity['region'] = 'NEL'
            item_entity['borough'] = site.get('borough')
            item_entity['pcn_network'] = site.get('pcn_network')
            item_entity['service_type'] = site.get('service_type')
            item_entity['code'] = site.get('code')
            item_entity['last_update'] = site.get('last_update')
            item_entity['stock-levels'] = stock_level
            item_entity['quantity_used'] = quantity_used
            item_entity['stock-levels-note'] = site.get(item_name + '-stock-levels-note')
            item_entity['daily_usage'] = daily_usage
            item_entity['rag'] = rag
            item_entity['mutual_aid_received'] = site.get(item_name + 'mutual_aid_received')
            item_entity['national_and_other_external_receipts'] = site.get(
                item_name + 'national_and_other_external_receipts')
            client.put(item_entity)


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


def get_sheet_data(site):
    safe_site_data = datastore.Entity(key=datastore.Client().key('Site', site['site']))
    fields = [
        'site',
        'face-visors-stock-levels',
        'face-visors-quantity_used',
        'face-visors-stock-levels-note',
        'face-visors-rag',
        'goggles-stock-levels',
        'goggles-quantity_used',
        'goggles-stock-levels-note',
        'goggles-rag',
        'masks-iir-stock-levels',
        'masks-iir-quantity_used',
        'masks-iir-stock-levels-note',
        'masks-iir-rag',
        'masks-ffp2-stock-levels',
        'masks-ffp2-quantity_used',
        'masks-ffp2-stock-levels-note',
        'masks-ffp2-rag',
        'masks-ffp3-stock-levels',
        'masks-ffp3-quantity_used',
        'masks-ffp3-stock-levels-note',
        'masks-ffp3-rag',
        'fit-test-solution-stock-levels',
        'fit-test-solution-quantity_used',
        'fit-test-solution-stock-levels-note',
        'fit-test-solution-rag',
        'fit-test-fullkit-stock-levels',
        'fit-test-fullkit-quantity_used',
        'fit-test-fullkit-stock-levels-note',
        'fit-test-fullkit-rag',
        'gloves-stock-levels',
        'gloves-quantity_used',
        'gloves-stock-levels-note',
        'gloves-rag',
        'gowns-stock-levels',
        'gowns-quantity_used',
        'gowns-stock-levels-note',
        'gowns-rag',
        'hand-hygiene-stock-levels',
        'hand-hygiene-quantity_used',
        'hand-hygiene-stock-levels-note',
        'hand-hygiene-rag',
        'apron-stock-levels',
        'apron-quantity_used',
        'apron-stock-levels-note',
        'apron-rag',
        'body-bags-stock-levels',
        'body-bags-quantity_used',
        'body-bags-stock-levels-note',
        'body-bags-rag',
        'coveralls-stock-levels',
        'coveralls-quantity_used',
        'coveralls-stock-levels-note',
        'coveralls-rag',
        'swabs-stock-levels',
        'swabs-quantity_used',
        'swabs-stock-levels-note',
        'swabs-rag',
        'fit-test-solution-55ml-stock-levels',
        'fit-test-solution-55ml-quantity_used',
        'fit-test-solution-55ml-stock-levels-note',
        'fit-test-solution-55ml-rag',
        'non-covid19-patient-number',
        'covid19-patient-number',
        'covid19-patient-number-suspected',
        'staff-number',
        'gowns-mutual_aid_received',
        'gowns-national_and_other_external_receipts',
        'coveralls-mutual_aid_received',
        'coveralls-national_and_other_external_receipts',
        'non-surgical-gowns-stock-levels',
        'non-surgical-gowns-quantity_used',
        'non-surgical-gowns-mutual_aid_received',
        'non-surgical-gowns-national_and_other_external_receipts',
        'non-surgical-gowns-stock-levels-note',
        'non-surgical-gowns-rag',
        'sterile-surgical-gowns-stock-levels',
        'sterile-surgical-gowns-quantity_used',
        'sterile-surgical-gowns-mutual_aid_received',
        'sterile-surgical-gowns-national_and_other_external_receipts',
        'sterile-surgical-gowns-stock-levels-note',
        'sterile-surgical-gowns-rag'
    ]

    for field in fields:
        try:
            safe_site_data[field] = site[field]
            print(f'field = {field} has value {safe_site_data[field]}')
        except Exception as e:
            print(e)
            print(f'problem with field = {field}')
    print(f'safe_site_data is {safe_site_data}')
    return safe_site_data


def get_child_sites(parent_code):
    client = datastore.Client()
    query = client.query(kind='Site')
    query.add_filter('parent', '=', parent_code)
    items = list(query.fetch())
    sites = {}
    for item in items:
        sites[item.get('site')]=item.get('code')
    return sites
