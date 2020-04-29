from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os

currentTime = datetime.datetime.now()


def search(request):
    print(request)

    request_args = request.args
    borough = ''
    pcn = ''
    service_type = ''

    if request_args:
        borough = request_args['borough']
        pcn = request_args['pcn']
        service_type = request_args['service_type']
    # Instantiates a client
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Site')
    query.add_filter('borough', '=', borough)
    query.add_filter('pcn', '=', pcn)
    query.add_filter('service_type', '=', service_type)
    # query.order = ['site']
    # query = datastore_client.query()
    results = list(query.fetch())
    print(results)
    sites = []
    for site in results:
        print(site['site'])
        sites.append(site['link'])

    return render_template('results.html', sites=sites)
