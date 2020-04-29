from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os

currentTime = datetime.datetime.now()

LINKS_SEARCH = 'links'
PARENT_SEARCH = 'parent'


def search(request):
    print(request)

    request_args = request.args
    search_type = 'Invalid search type'
    result_label = 'No results'

    # Instantiates a client
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Site')

    if request_args:
        if request_args['search_type'] == LINKS_SEARCH:
            search_type = 'Search for community sites'
            borough = request_args['borough']
            pcn = request_args['pcn']
            service_type = request_args['service_type']
            results_label = f'Results using filter values  Borough: {borough}  PCN: {pcn}  Service Type: {service_type}'
            query.add_filter('borough', '=', borough)
            query.add_filter('pcn', '=', pcn)
            query.add_filter('service_type', '=', service_type)
            results = list(query.fetch())
        if request_args['search_type'] == PARENT_SEARCH:
            search_type = 'Search for child sites'
            parent = request_args['parent']
            result_label = f'Results using filter values Parent: {parent}'
            query.add_filter('parent', '=', parent)
            results = list(query.fetch())
    results = list(query.fetch())
    print(results)
    sites = []
    for site in results:
        print(site['site'])
        sites.append(site['link'])

    return render_template('results.html',
                           sites=results,
                           assets='https://storage.googleapis.com/ppe-inventory',
                           search_type=search_type,
                           results_label=result_label)
