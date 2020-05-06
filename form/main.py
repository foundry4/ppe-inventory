from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os

currentTime = datetime.datetime.now()


def form(request):
    name = request.cookies.get('site')
    code = request.cookies.get('code')

    client = datastore.Client()

    site = None
    post = False
    if name and code:
        site = get_site(name, code, client)

    if site and request.method == 'POST':
        update_site(site, client, request, code)
        publish_update(get_sheet_data(site))
        post = True

    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain = os.getenv('DOMAIN')
    form_action = f'https://{domain}/form'
    dashboard_link = f'https://{domain}/dashboard'

    if post:
        template = 'success.html'
    elif site and 'acute' in site.keys() and site['acute'] == 'yes':
        template = 'form.html'
    elif site:
        template = 'community_form.html'
    else:
        template = 'error.html'

    # template = 'success.html' if post else 'form.html' if site else 'error.html'
    print(f"Rendering {template}")

    response = make_response(render_template(template,
                                             site=site,
                                             form_action=form_action,
                                             dashboard_link=dashboard_link,
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))

    if site:
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


def update_ppe_item(site, client, request):
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
        for item in item_names:
            if quantity_used > 0:
                client = datastore.Client()
            query = client.query(kind='Ppe-Item')
            query.add_filter('provider', '=', site.get('site'))
            query.add_filter('item_name', '=', item)
            items = list(query.fetch())
            print(f"found {len(items)} for site {site.get('site')} and item {item}")
            if len(items) == 0:
                item_entity = datastore.Entity(client.key('Ppe-Item'))
                item_entity['provider'] = site.get('site')
                item_entity['item_name'] = item
                item_entity['region'] = 'NEL'
                item_entity['borough'] = site.get('borough')
                item_entity['pcn_network'] = site.get('pcn_network')
            else:
                item_entity = items[0]
            stock_level = int(site.get(item + '-stock-levels')) if site.get(item + '-stock-levels') else 0
            quantity_used = int(site.get(item + '-quantity_used')) if site.get(item + '-quantity_used') else 0
            daily_usage = np.nan if quantity_used == 0 else stock_level / quantity_used
            rag = 'under_one' if daily_usage < 1 else \
                'one_two' if daily_usage < 2 else \
                    'two_three' if daily_usage < 3 else \
                        'less-than-week' if daily_usage < 7 else \
                            'more-than-week'
            item_entity['last_update'] = site.get('last_update')
            item_entity['stock-levels'] = stock_level
            item_entity['quantity_used'] = quantity_used
            item_entity['stock-levels-note'] = site.get(item + '-stock-levels-note')
            item_entity['daily_usage'] = daily_usage
            item_entity['rag'] = rag
            item_entity['mutual_aid_received'] = site.get(item + 'mutual_aid_received')
            item_entity['national_and_other_external_receipts'] = site.get(
                item + 'national_and_other_external_receipts')
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
        'coveralls-national_and_other_external_receipts'
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
