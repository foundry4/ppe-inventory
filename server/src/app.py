import json
import datetime
from datetime import timezone

import pytz
from flask import Flask, render_template, make_response, request, redirect, url_for, g, flash, Markup
import os

from flask_oidc import OpenIDConnect
from google.cloud import datastore
from google.cloud import pubsub_v1
from okta import UsersClient
# import server.src.db as db

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

client_secrets = {'web': {
    'client_id': os.getenv('OKTA_CLIENT_ID'),
    'client_secret': os.getenv('OKTA_CLIENT_SECRET'),
    'auth_uri': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default/v1/authorize',
    'token_uri': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default/v1/token',
    'issuer': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default',
    'userinfo_uri': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default/v1/userinfo',
    'redirect_uris': os.getenv('OIDC_REDIRECT_URIS')
}}

with open('client_secrets.json', 'w') as fp:
    json.dump(client_secrets, fp)

app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
app.config['OIDC_COOKIE_SECURE'] = os.getenv('OIDC_COOKIE_SECURE')
app.config['OIDC_CALLBACK_ROUTE'] = os.getenv('OIDC_CALLBACK_ROUTE')
app.config['OIDC_SCOPES'] = ["openid", "email", "profile"]
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

oidc = OpenIDConnect(app)

okta_client = UsersClient(os.getenv('OKTA_ORG_URL'), os.getenv('OKTA_AUTH_TOKEN'))
datastore_client = datastore.Client()

LINKS_SEARCH = 'links'
CHILDREN_SEARCH = 'children'


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Europe/London'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sites')
@oidc.require_login
def sites(client=datastore_client, request_param=request):
    # Extract sets of values from borough, service_type and pcn query params
    request_args = request_param.args
    selected_boroughs = get_set_from_args_str(request_args.get('borough', ''))
    selected_service_types = get_set_from_args_str(request_args.get('service_type', ''))
    selected_pcns = get_set_from_args_str(request_args.get('pcn', ''))

    # Get all sites, boroughs, service_types and pcns
    query = client.query(kind='Site')
    all_sites = list(query.fetch())
    boroughs = get_boroughs(all_sites)
    service_types = get_service_types(all_sites)
    pcns = get_pcns(all_sites, selected_boroughs, selected_service_types)

    results = get_filtered_sites(all_sites, selected_boroughs, selected_service_types, selected_pcns)

    sites_to_display = []

    for result in results:
        if result.get('last_update') is None:
            dt = ' - not recorded'
        else:
            utc_dt = result['last_update']
            dt = utc_to_local(utc_dt).strftime("%H:%M, %a %d %b %Y")
        sites_to_display.append({'link': result['link'], 'provider': result['site'], 'dt': dt, 'code': result['code']})

    response = make_response(render_template('sites.html',
                                             sites=sites_to_display,
                                             boroughs=boroughs,
                                             selected_boroughs=selected_boroughs,
                                             service_types=service_types,
                                             selected_service_types=selected_service_types,
                                             pcns=pcns,
                                             selected_pcns=selected_pcns))
    return response


def get_ppe_items(item_names, items):
    return [get_ppe_item(item_names, name, items) for name in item_names]


def get_ppe_item(item_names, item_name, items):
    item_count = sum(item.get('item_name') == item_name for item in items)
    if item_count > 0:
        named_items = [item for item in items if item.get('item_name') == item_name]
        ppe_item = {
            'name': item_name,
            'display_name': item_names[item_name],
            'under_one': '{:.0%}'.format(sum(1 for item in named_items if item.get('rag') == 'under_one') / item_count),
            'one_two': '{:.0%}'.format(sum(1 for item in named_items if item.get('rag') == 'one_two') / item_count),
            'two_three': '{:.0%}'.format(sum(1 for item in named_items if item.get('rag') == 'two_three') / item_count),
            'less-than-week': '{:.0%}'.format(
                sum(1 for item in named_items if item.get('rag') == 'less-than-week') / item_count),
            'more-than-week': '{:.0%}'.format(
                sum(1 for item in named_items if item.get('rag') == 'more-than-week') / item_count),
        }

        rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
        max_item = 'under_one'
        for rag in rags:
            if ppe_item[rag] > ppe_item[max_item]:
                max_item = rag
        ppe_item['highlight'] = max_item
        return ppe_item

    # return empty item if no values avialable
    return {
        'name': item_name,
        'display_name': item_names[item_name],
        'under_one': '{:.0%}'.format(0),
        'one_two': '{:.0%}'.format(0),
        'two_three': '{:.0%}'.format(0),
        'less-than-week': '{:.0%}'.format(0),
        'more-than-week': '{:.0%}'.format(0),
        'highlight': 'under_one'}


def sort_ppe_items(items):
    rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
    sorted_items = sorted(items, key=lambda x: [x[r] for r in rags])
    # print([i['highlight'] for i in sorted_items], file=sys.stderr)
    return_items = []
    for r in rags:
        # print(r, file=sys.stderr)
        for item in sorted_items:
            if item['highlight'] == r:
                return_items.append(item)

    return return_items


@app.route('/dashboards')
@oidc.require_login
def dashboards(client=datastore_client, request_param=request):
    # Extract sets of values from borough, service_type and pcn query params
    request_args = request_param.args
    selected_boroughs = get_set_from_args_str(request_args.get('borough', ''))
    selected_service_types = get_set_from_args_str(request_args.get('service_type', ''))
    selected_pcns = get_set_from_args_str(request_args.get('pcn', ''))

    # Get all sites, boroughs, service_types and pcns
    query = client.query(kind='Site')
    all_sites = list(query.fetch())
    boroughs = get_boroughs(all_sites)
    service_types = get_service_types(all_sites)
    pcns = get_pcns(all_sites, selected_boroughs, selected_service_types)

    sites = get_sites()

    updated_sites = [site.get('last_update') for site in sites if
                     site.get('last_update') and site.get('last_update').date() >= (
                             datetime.date.today() - datetime.timedelta(days=7))]

    print(f"{len(updated_sites)} of {len(sites)} sites have been updated.")

    template = 'dashboards.html'

    item_names = {'face-visors': 'Face Visors',
                  'goggles': 'Goggles',
                  'masks-iir': 'Masks (IIR)',
                  'masks-ffp2': 'Masks (FFP2)',
                  'masks-ffp3': 'Masks (FFP3)',
                  'gloves': 'Gloves',
                  'gowns': 'Gowns',
                  'hand-hygiene': 'Hand Hygiene',
                  'apron': 'Apron'}

    print(f"Rendering {template}")

    db_items = get_ppe_items_from_db()

    results = get_filtered_sites(db_items, selected_boroughs, selected_service_types, selected_pcns)

    ppe_items = get_ppe_items(item_names, results)

    sorted_items = sort_ppe_items(ppe_items)

    # print(sorted_items, file=sys.stderr)
    response = make_response(render_template(template,
                                             item_count=len(sorted_items),
                                             items=sorted_items,
                                             site_count=len(sites),
                                             updated_site_count=len(updated_sites),
                                             boroughs=boroughs,
                                             selected_boroughs=selected_boroughs,
                                             service_types=service_types,
                                             selected_service_types=selected_service_types,
                                             pcns=pcns,
                                             selected_pcns=selected_pcns
                                             ))
    return response


def get_set_from_args_str(args_str):
    result = set()
    if args_str:
        items = args_str[1:-1].split(',')
        for i in items:
            i = i.strip()
            result.add(i)
    return result


def get_boroughs(all_sites):
    boroughs = set()
    for s in all_sites:
        if 'borough' in s:
            if s.get('borough') != '':
                boroughs.add(s['borough'])
    return sorted(boroughs)


def get_service_types(all_sites):
    service_types = set()
    for s in all_sites:
        if 'service_type' in s:
            if s.get('service_type') != '':
                service_types.add(s['service_type'])
    return sorted(service_types)


def get_pcns(all_sites, selected_boroughs, selected_service_types):
    print(selected_boroughs)
    print(selected_service_types)
    pcns = set()
    for s in all_sites:
        passed_filter = True
        if 'pcn_network' in s:
            if s.get('pcn_network') == '':
                passed_filter = False
            if selected_boroughs:
                if 'borough' in s:
                    if s.get('borough') not in selected_boroughs:
                        passed_filter = False
            if selected_service_types:
                if 'service_type' in s:
                    if s.get('service_type') not in selected_service_types:
                        passed_filter = False
            if passed_filter:
                pcns.add(s['pcn_network'])
    return sorted(pcns)


def get_filtered_sites(all_sites, selected_boroughs, selected_service_types, selected_pcns):
    results = []
    # Apply filter for all optional query params
    for s in all_sites:
        passed_filter = True
        if selected_boroughs:
            if s.get('borough'):
                if s.get('borough') not in selected_boroughs:
                    passed_filter = False
            else:
                passed_filter = False
        if selected_service_types:
            if s.get('service_type'):
                if s.get('service_type') not in selected_service_types:
                    passed_filter = False
            else:
                passed_filter = False
        if selected_pcns:
            if s.get('pcn_network'):
                if s.get('pcn_network') not in selected_pcns:
                    passed_filter = False
            else:
                passed_filter = False
        if passed_filter:
            results.append(s)
    return results


def get_filter_result(site_to_filter, field, values):
    if field in site_to_filter:
        if site_to_filter[field] not in values:
            return False
    else:
        return False


def get_links(service_type, borough, pcn, client=datastore_client):
    query = client.query(kind='Site')
    query.add_filter('borough', '=', borough)
    query.add_filter('pcn_network', '=', pcn)
    query.add_filter('service_type', '=', service_type)
    results = list(query.fetch())
    return results


@app.route('/sites/<site_param>')
def site(site_param):
    query = datastore_client.query(kind='Site')
    query.add_filter('code', '=', site_param)
    result = list(query.fetch())
    if result:
        return render_template('site.html', site=result[0])
    else:
        flash(f'The site with code: {site_param} cannot be found', 'error')
        return redirect(url_for('index'))


@app.route('/forms/<site_param>')
def form(site_param):
    query = datastore_client.query(kind='Site')
    query.add_filter('code', '=', site_param)
    result = list(query.fetch())
    if result:
        return render_template('form.html', site=result[0])
    else:
        flash(f'The site with code: {site_param} cannot be found', 'error')
        return redirect(url_for('index'))


@app.route('/sites/<site_param>', methods=["POST"])
def site_update(site_param, client=datastore_client, request_param=request):
    site_to_update = get_site(site_param, client)
    if site_to_update:
        update_site(client=client, site_to_update=site_to_update, request_param=request_param)
        publish_update(get_sheet_data(site_to_update))
        site_name = site_to_update['provider']
        message = Markup(f'<a href="/sites/{site_param}">{site_name}</a>')
        flash("Site " + message + " was updated.", 'success')
    else:
        flash(f'There was a problem updating site with code: {site_param}.', 'error')
    return redirect(url_for('index'))


@app.route('/login')
@oidc.require_login
def login():
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    oidc.logout()
    return redirect(url_for('index'))


@app.before_request
def inject_user_into_each_request():
    if oidc.user_loggedin:
        g.user = okta_client.get_user(str(oidc.user_getfield('sub')))
    else:
        g.user = None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def get_site(code, client):
    query = client.query(kind='Site')
    query.add_filter('code', '=', code)
    result = list(query.fetch())
    if result:
        return result[0]
    return None


def update_site(site_to_update, client, request_param):
    # Values NOT to change
    site_name = site_to_update.key.name
    site_code = site_to_update['code']
    acute_status = site_to_update['acute']
    # Update the site inc timestamp while preserving selected values
    site_to_update.update(request_param.form)
    site_to_update["last_update"] = datetime.datetime.now()
    site_to_update['site'] = site_name
    site_to_update['acute'] = acute_status
    site_to_update['code'] = site_code
    client.put(site_to_update)


def publish_update(site_to_update):
    # Publish a message to update the Google Sheet:
    message = {}
    message.update(site_to_update)
    message['last_update'] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%H:%M %d %B %y')
    publisher = pubsub_v1.PublisherClient()
    project_id = os.getenv("PROJECT_ID")
    topic_path = publisher.topic_path(project_id, 'form-submissions')
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    print(f"Published update to site {site_to_update.key.name}: {future.result()}")


def get_sheet_data(site_to_update):
    safe_site_data = datastore.Entity(key=datastore.Client().key('Site', site_to_update['site']))
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
            safe_site_data[field] = site_to_update[field]
        except Exception as e:
            print(f'Exception {e} triggered when preparing safe data to pass to spreadsheet')
    return safe_site_data


def get_sites():
    client = datastore.Client()
    query = client.query(kind='Site')
    query.add_filter('acute', '=', 'no')
    sites = list(query.fetch())

    return sites


def get_site(name, code):
    client = datastore.Client()
    print(f"Getting site: {name}/{code}")
    key = client.key('Site', name)
    site = client.get(key)
    if site and site.get('code') == code:
        return site

    print(f"No site detected in db: {name}/{code}")
    return None


def get_ppe_items_from_db():
    client = datastore.Client()
    query=client.query(kind='Ppe-Item')
    query.add_filter('quantity_used', '>', 0)
    items = list(query.fetch())
    return items
