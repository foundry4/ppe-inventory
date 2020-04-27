import datetime
import os
from flask import make_response, render_template
from dashboard.db import get_sites, get_site


def dashboard(request):

    name = request.args.get('site')
    code = request.args.get('code')

    if name and code:
        response = render_site(name, code)
    else:
        response = render_dashboard()
    return response


def render_dashboard():
    sites = get_sites()
    template = 'dashboard.html'

    print(f"Rendering {template}")
    items = get_ppe_items(sites)
    response = make_response(render_template(template,
                                             items=items,
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))
    return response


def render_site(name, code):
    site = get_site(name, code)
    template = 'site.html'
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain = os.getenv('DOMAIN')
    form_action = f'https://{domain}/dashboard?site={name}&code={code}'
    print(f"Rendering {template}")
    items = get_ppe_items(site)
    sorted_items = sort_ppe_items(items)
    response = make_response(render_template(template,
                                             items=sorted_items,
                                             form_action=form_action,
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))
    return response


def get_ppe_item(name, sites):
    site_count = len(sites)
    ppe_item = {
        'name': name,
        'under_one': '{:.2%}'.format( sum(1 for site in sites if site.get((name + '-RAG').lower()) == 'one-or-less') / site_count),
        'one_two': '{:.2%}'.format(sum(1 for site in sites if site.get(name + '-RAG') == 'one_two') / site_count),
        'two_three': '{:.2%}'.format(sum(1 for site in sites if site.get((name + '-RAG').lower()) == 'two-three') / site_count),
        'over_three': '{:.2%}'.format(sum(1 for site in sites if site.get((name + '-RAG').lower()) == 'over_three') / site_count),
    }

    max_item = 'under_one'
    for prop in ['one_two', 'two_three', 'over_three']:
        if ppe_item[prop] > ppe_item[max_item]:
            max_item = prop
    ppe_item['highlight'] = max_item
    return ppe_item


def get_ppe_items(sites):
    for name in 'Face visors',\
             'Goggles',\
             'Masks (IIR)',\
             'Masks (FFP2)',\
             'Masks (FFP3)',\
             'Fit test (solution)',\
             'Fit test (full kit)',\
             'Gloves',\
             'Gowns',\
             'Hand hygiene',\
             'Apron':

        item = get_ppe_item(name, sites)
        yield item


def sort_ppe_items(items):
    for rag in 'under_one', 'one_two', 'two_three', 'over_three':
        yield [item for item in items.sort(key= lambda x:x[rag]) if item['highlight'] == rag]
