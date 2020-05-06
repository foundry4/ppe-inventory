import json
import datetime
import urllib
from ast import literal_eval
from datetime import timezone

import pytz
from flask import Flask, render_template, make_response, request, redirect, url_for, g, flash, Markup
import os

from flask_oidc import OpenIDConnect
from google.cloud import datastore
from google.cloud import pubsub_v1
from okta import UsersClient

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
def sites(client=datastore_client, request_param=request):
    # Get all sites
    query = client.query(kind='Site')
    all_sites = list(query.fetch())

    request_args = request_param.args
    results = get_filtered_sites(all_sites, request_args)

    sites_to_display = []

    for result in results:
        if result.get('last_update') is None:
            dt = ' - not recorded'
        else:
            utc_dt = result['last_update']
            dt = utc_to_local(utc_dt).strftime("%H:%M, %a %d %b %Y")
        sites_to_display.append({'link': result['link'], 'provider': result['site'], 'dt': dt})

    return render_template('sites.html', sites=sites_to_display)


def get_filtered_sites(all_sites, filter_args):
    results = []
    borough_args = filter_args.get('borough', None)
    boroughs = []
    if borough_args:
        print(f'borough_args = {borough_args}')
        boroughs = borough_args.split(',')
        for b in boroughs:
            print(b)
            b = b.strip()

    pcn_args = filter_args.get('pcn', None)
    pcns = []
    if pcn_args:
        print(f'pcn_args = {pcn_args}')
        pcns = pcn_args.split(',')
        for p in pcns:
            print(p)
            p = p.strip()

    service_type_args = filter_args.get('service_type', None)
    service_types = []
    if service_type_args:
        print(f'service_type_args = {service_type_args}')
        service_types = service_type_args.split(',')
        for s in service_types:
            print(s)
            s = s.strip()

    # Apply filter for all optional query params
    for s in all_sites:
        passed_filter = True
        if borough_args:
            if "borough" in s:
                if s['borough'] not in boroughs:
                    passed_filter = False
            else:
                passed_filter = False
        if pcn_args:
            if "pcn_network" in s:
                if s['pcn_network'] not in pcns:
                    passed_filter = False
            else:
                passed_filter = False
        if service_type_args:
            if "service_type" in s:
                if s['service_type'] not in service_types:
                    passed_filter = False
            else:
                passed_filter = False
        if passed_filter:
            print(f'{s.get("borough", "****")}   {s.get("pcn_network", "****")}   {s.get("service_type", "****")}')
            results.append(s)

    return results


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
        site_name = site_to_update['site']
        message = Markup(f'<a href="/sites/{site_param}">{site_name}</a>')
        flash("Site " + message + " was updated.", 'success')
    else:
        flash(f'There was a problem updating site with code: {site_param}.', 'error')
    return redirect(url_for('index'))


@app.route('/dashboard')
@oidc.require_login
def dashboard():
    # This is where we get the dashboard data
    return render_template('dashboard.html')


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
