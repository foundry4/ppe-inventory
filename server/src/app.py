import datetime
import json
import os
from datetime import timezone
# Imports the Cloud Logging client library
import google.cloud.logging
import pytz
from flask import Flask, render_template, make_response, request, redirect, url_for, flash
from flask_oidc import OpenIDConnect
from google.cloud import datastore
from okta import UsersClient
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sys

users = {
    os.getenv('USER_NAME'): generate_password_hash(os.getenv('PASSWORD'))
}

app = Flask(__name__)

auth = HTTPBasicAuth()

# This is required by flask for encrypting cookies and other features
app.secret_key = os.getenv('APP_SECRET_KEY')

# The OIDC config looks for a json file so one is created from environment variables
client_secrets = {'web': {
    'client_id': os.getenv('OKTA_CLIENT_ID'),
    'client_secret': os.getenv('OKTA_CLIENT_SECRET'),
    'auth_uri': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default/v1/authorize',
    'token_uri': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default/v1/token',
    'issuer': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default',
    'userinfo_uri': f'{os.getenv("OKTA_ORG_URL")}/oauth2/default/v1/userinfo',
    'redirects_uris': os.getenv('OIDC_REDIRECT_URIS')
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

# Client for Google's Datastore
datastore_client = datastore.Client()

# Instantiates a Google logging client
logging_client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
logging_client.get_default_handler()
logging_client.setup_logging()


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/dashboards/items/<item_param>')
@auth.login_required
def dashboard_items(item_param, request_param=request):
    request_args = request_param.args
    selected_boroughs = get_set_from_args_str(request_args.get('borough', ''))
    selected_service_types = get_set_from_args_str(request_args.get('service_type', ''))
    selected_pcns = get_set_from_args_str(request_args.get('pcn', ''))
    selected_date_range = 'last_seven_days'

    query = datastore_client.query(kind='Site')
    all_sites = list(query.fetch())
    boroughs = get_boroughs(all_sites)
    service_types = get_service_types(all_sites)
    pcns = get_pcns(all_sites, selected_boroughs, selected_service_types)
    stock_items = get_stock_items_by_item_name_from_db(item_param)

    filtered_stock_items = \
        get_filtered_sites(
            stock_items,
            selected_boroughs,
            selected_service_types,
            selected_pcns,
            selected_date_range)

    rags = ('', 'under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
    filtered_stock_items.sort(key=lambda x: rags.index(x.get('rag')))

    print(f"found {len(stock_items)} stock items")

    rag_color_codes = get_rag_color_codes()
    item_names = get_item_names()

    rag_item_sums = {
        'under_one':
            sum([1 for item in filtered_stock_items if
                 item.get('rag') == 'under_one' and item.get('quantity_used') > 0]),
        'one_two':
            sum([1 for item in filtered_stock_items if item.get('rag') == 'one_two' and item.get('quantity_used') > 0]),
        'two_three':
            sum([1 for item in filtered_stock_items if
                 item.get('rag') == 'two_three' and item.get('quantity_used') != 0]),
        'less-than-week':
            sum([1 for item in filtered_stock_items if
                 item.get('rag') == 'less-than-week' and item.get('quantity_used') > 0]),
        'more-than-week':
            sum([1 for item in filtered_stock_items if
                 item.get('rag') == 'more-than-week' and item.get('quantity_used') > 0]),
    }

    rag_labels = get_rag_labels()
    if stock_items:
        return render_template('item.html',
                               item=item_param,
                               stock_items=[item for item in filtered_stock_items if item['quantity_used'] > 0],
                               rag_item_sums=rag_item_sums,
                               item_names=item_names,
                               color_codes=rag_color_codes,
                               rag_labels=rag_labels,
                               boroughs=boroughs,
                               selected_boroughs=selected_boroughs,
                               service_types=service_types,
                               selected_service_types=selected_service_types,
                               pcns=pcns,
                               selected_pcns=selected_pcns,
                               baseUrl=item_param
                               )
    else:
        flash(f'No stock_items of {item_param} can be found', 'error')
        return redirect(url_for('index'))


@app.route('/')
def home():
    return redirect('/dashboards')


@app.route('/dashboards')
@auth.login_required
def dashboards(client=datastore_client, request_param=request):
    # Extract sets of values from borough, service_type and pcn query params
    request_args = request_param.args
    selected_boroughs = get_set_from_args_str(request_args.get('borough', ''))
    selected_service_types = get_set_from_args_str(request_args.get('service_type', ''))
    selected_pcns = get_set_from_args_str(request_args.get('pcn', ''))

    # Get all sites, boroughs, service_types and pcns
    all_sites = get_sites(datastore_client)
    boroughs = get_boroughs(all_sites)
    service_types = get_service_types(all_sites)
    pcns = get_pcns(all_sites, selected_boroughs, selected_service_types)
    selected_date_range = 'anytime'

    filtered_sites = get_filtered_sites(
        all_sites,
        selected_boroughs,
        selected_service_types,
        selected_pcns,
        selected_date_range)

    updated_sites = [site.get('last_update') for site in filtered_sites if
                     site.get('last_update') and site.get('last_update').date() >= (
                             datetime.date.today() - datetime.timedelta(days=7))]

    print(f"{len(updated_sites)} of {len(filtered_sites)} sites have been updated.")

    template = 'dashboards.html'
    item_names = get_item_names()

    print(f"Rendering {template}")

    db_items = get_ppe_items_from_db(datastore_client)
    print(f"db items: {db_items}")
    results = get_filtered_sites(
        db_items,
        selected_boroughs,
        selected_service_types,
        selected_pcns,
        'anytime')

    ppe_items = get_ppe_items(item_names, results)

    sorted_items = sort_ppe_items(ppe_items)

    # print(sorted_items, file=sys.stderr)
    response = make_response(render_template(template,
                                             item_count=len(sorted_items),
                                             items=sorted_items,
                                             site_count=len(filtered_sites),
                                             updated_site_count=len(updated_sites),
                                             boroughs=boroughs,
                                             selected_boroughs=selected_boroughs,
                                             service_types=service_types,
                                             selected_service_types=selected_service_types,
                                             pcns=pcns,
                                             selected_pcns=selected_pcns,
                                             baseUrl='dashboards'
                                             ))
    return response


@app.route('/sites')
@auth.login_required
def sites(client=datastore_client, request_param=request):
    # Extract sets of values from borough, service_type and pcn query params
    request_args = request_param.args
    selected_boroughs = get_set_from_args_str(request_args.get('borough', ''))
    selected_service_types = get_set_from_args_str(request_args.get('service_type', ''))
    selected_pcns = get_set_from_args_str(request_args.get('pcn', ''))
    selected_date_range = request_args.get('date_range','last_seven_days')
    print(f'selected_date_range:{selected_date_range}', file=sys.stderr)
    # Get all sites, boroughs, service_types and pcns
    # query = client.query(kind='Site')
    all_sites = get_sites(datastore_client)
    boroughs = get_boroughs(all_sites)
    service_types = get_service_types(all_sites)
    pcns = get_pcns(all_sites, selected_boroughs, selected_service_types)

    # Get filtered sites
    results = get_filtered_sites(all_sites,
                                 selected_boroughs,
                                 selected_service_types,
                                 selected_pcns,
                                 selected_date_range)

    # Construct collection of representations of sites to pass to template
    seven_days_ago = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('Europe/London')) - datetime.timedelta(
        days=7)

    response = make_response(render_template('sites.html',
                                             sites=results,
                                             all_site_count = len(all_sites),
                                             filtered_sites_count = len(results),
                                             boroughs=boroughs,
                                             selected_boroughs=selected_boroughs,
                                             service_types=service_types,
                                             selected_service_types=selected_service_types,
                                             pcns=pcns,
                                             selected_pcns=selected_pcns,
                                             selected_date_range=selected_date_range,
                                             baseUrl='sites'))
    return response


@app.route('/sites/<site_param>')
@auth.login_required
def site(site_param):
    provider = get_provider_by_code_from_db(site_param)
    stock_items = get_stock_items_by_provider_from_db(provider)
    rag_labels= get_rag_labels()
    stock_items.sort(key=lambda x: list(rag_labels).index(x.get('rag')))

    if provider:
        return render_template('site.html',
                               site=provider,
                               stock_items= [item for item in stock_items if item['quantity_used'] > 0],
                               stock_items_count=len(stock_items),
                               item_names=get_item_names(),
                               color_codes=get_rag_color_codes(),
                               rag_labels=rag_labels)
    else:
        flash(f'The site with code: {site_param} cannot be found', 'error')
        return redirect(url_for('index'))


def get_stock_items_by_provider_from_db(provider):
    query = datastore_client.query(kind='Ppe-Item')
    query.add_filter('provider', '=', provider.get('provider'))
    stock_items = list(query.fetch())
    print(f"found {len(stock_items)} stock items")
    return stock_items


def get_stock_items_by_item_name_from_db(item_name):
    query = datastore_client.query(kind='Ppe-Item')
    query.add_filter('item_name', '=', item_name)
    stock_items = list(query.fetch())
    print(f"found {len(stock_items)} stock items")
    return stock_items


def get_provider_by_code_from_db(site_param):
    query = datastore_client.query(kind='Site')
    query.add_filter('code', '=', site_param)
    providers = list(query.fetch())
    provider = providers[0]
    print(f"provider:{provider.get('site')}")
    return provider


def get_rag_labels():
    rag_labels = {
        '': 'N/A',
        'under_one': 'Up to 1 day',
        'one_two': '1-2 days',
        'two_three': '2-3 days',
        'less-than-week': '3-7 days',
        'more-than-week': 'Over 1 week',

    }
    return rag_labels


def get_rag_color_codes():
    rag_color_codes = {
        'under_one': 'maroon',
        'one_two': 'red',
        'two_three': 'amber',
        'less-than-week': 'lightgreen',
        'more-than-week': 'green',
    }
    return rag_color_codes


@app.route('/login')
@oidc.require_login
def login():
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    oidc.logout()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def get_sites(client):
    query = client.query(kind='Site')
    query.add_filter('acute', '=', 'no')
    db_sites = list(query.fetch())

    return db_sites


def get_site(code, client):
    print(code)
    query = client.query(kind='Site')
    query.add_filter('code', '=', code)
    result = list(query.fetch())
    print(result)
    if result:
        return result[0]
    return None


def get_ppe_items_from_db(client):
    query = client.query(kind='Ppe-Item')
    query.add_filter('quantity_used', '>', 0)
    items = list(query.fetch())
    return items


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Europe/London'))


def get_ppe_items(item_names, items):
    return [get_ppe_item(item_names, name, items) for name in item_names]


def get_ppe_item(item_names, item_name, items):
    item_count = sum(item.get('item_name') == item_name for item in items)
    rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
    if item_count > 0:
        named_items = [item for item in items if item.get('item_name') == item_name]
        ppe_item = {
            'name': item_name,
            'display_name': item_names[item_name],
            'under_one': sum(1 for item in named_items if item.get('rag') == 'under_one') / item_count,
            'one_two': sum(1 for item in named_items if item.get('rag') == 'one_two') / item_count,
            'two_three': sum(1 for item in named_items if item.get('rag') == 'two_three') / item_count,
            'less-than-week': sum(1 for item in named_items if item.get('rag') == 'less-than-week') / item_count,
            'more-than-week': sum(1 for item in named_items if item.get('rag') == 'more-than-week') / item_count,
        }

        max_item = 'under_one'
        for rag in rags:
            if ppe_item[rag] > ppe_item[max_item]:
                max_item = rag
        ppe_item['highlight'] = max_item
        return ppe_item

    # return empty item if no values available
    return {
        'name': item_name,
        'display_name': item_names[item_name],
        'under_one': 0,
        'one_two': 0,
        'two_three': 0,
        'less-than-week': 0,
        'more-than-week': 0,
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


def get_filtered_sites(all_sites, selected_boroughs, selected_service_types, selected_pcns, selected_date_range):
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
        if selected_date_range:
            if not is_site_in_date_range(s, selected_date_range):
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


def is_site_in_date_range(site, selected_date_range):
    if selected_date_range == 'anytime':
        return True

    seven_days_ago = datetime.datetime.utcnow() \
        .replace(tzinfo=pytz.timezone('Europe/London')) \
        - datetime.timedelta(days=7)

    if selected_date_range == 'last_seven_days' \
            and site \
            and site.get('last_update') \
            and site.get('last_update') >= seven_days_ago:
        return True

    if selected_date_range == 'more_than_seven_days' \
            and site \
            and site.get('last_update') \
            and site.get('last_update') < seven_days_ago:
        return True

    return False

def get_item_names():
    item_names = {'face-visors': 'Face Visors',
                  'goggles': 'Goggles',
                  'masks-iir': 'Masks (IIR)',
                  'masks-ffp2': 'Masks (FFP2)',
                  'masks-ffp3': 'Masks (FFP3)',
                  'gloves': 'Gloves',
                  'gowns': 'Gowns',
                  'hand-hygiene': 'Hand Hygiene',
                  'apron': 'Aprons'}
    return item_names
