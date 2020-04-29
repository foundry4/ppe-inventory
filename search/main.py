from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os

currentTime = datetime.datetime.now()

LINKS_SEARCH = 'links'
CHILDREN_SEARCH = 'children'


def search(request):
    print(request)

    request_args = request.args
    search_type = 'Invalid search type'
    result_label = 'No results'

    # Instantiates a client
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Site')
    results=[]
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
    sites = []
    for result in results:
        sites.append({'link': result['link'], 'site': result['site']})

    return render_template('results.html',
                           sites=sites,
                           assets='https://storage.googleapis.com/ppe-inventory',
                           search_type=search_type,
                           result_label=result_label)
