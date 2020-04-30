import datetime
import os
from flask import make_response, render_template
from dashboard.db import get_sites, get_site
import sys
import pandas as pd


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
    df = get_dataframe(sites)
    items = get_ppe_items(sites,df)
    sorted_items = sort_ppe_items(items)
    response = make_response(render_template(template,
                                             items=sorted_items,
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
    print(sorted_items)
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
    rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')

    df = pd.DataFrame([site.get('Site') for site in sites])
    print(df, file=sys.stderr)

    df_rag = pd.DataFrame(rags)
    df_rag['stock-levels'] = 0
    df_rag['stock-levels']['under_one'] = \
        sum(1 for site in sites if site.get(name + '-stock-levels') and site.get(name + '-stock-levels') < 1)
    df_rag['stock-levels']['one_two'] = sum(
        1 for site in sites if site.get(name + '-stock-levels') and 1 <=site.get(name + '-stock-levels') < 2)
    df_rag['stock-levels']['two_three'] = sum(
        1 for site in sites if site.get(name + '-stock-levels') and 2 <= site.get(name + '-stock-levels') < 3)
    df_rag['stock-levels']['less-than-week'] = sum(
        1 for site in sites if site.get(name + '-stock-levels') and 3 <= site.get(name + '-stock-levels') < 7)
    df_rag['stock-levels']['more-than-week'] = sum(
        1 for site in sites if site.get(name + '-stock-levels') and 7 <= site.get(name + '-stock-levels'))

    df_rag['quantity_used'] = 0
    df_rag['quantity_used']['under_one'] = \
        sum(1 for site in sites if site.get(name + '-quantity_used') and site.get(name + '-quantity_used') < 1)
    df_rag['quantity_used']['one_two'] = sum(
        1 for site in sites if site.get(name + '-quantity_used') and 1 <=site.get(name + '-quantity_used') < 2)
    df_rag['quantity_used']['two_three'] = sum(
        1 for site in sites if site.get(name + '-quantity_used') and 2 <= site.get(name + '-quantity_used') < 3)
    df_rag['quantity_used']['less-than-week'] = sum(
        1 for site in sites if site.get(name + '-quantity_used') and 3 <= site.get(name + '-quantity_used') < 7)
    df_rag['quantity_used']['more-than-week'] = sum(
        1 for site in sites if site.get(name + '-quantity_used') and 7 <= site.get(name + '-quantity_used'))

    df_rag['ratio'] = df['stock-levels'] / df['quantity_count']

    ppe_item = {
        'name': name,
        'under_one': '{:.2%}'.format(sum(1 for site in sites if site.get((name + '-stock-levels') / site.get((name + '-quantity_used').lower())) < 1) / site_count),
        'one_two': '{:.2%}'.format(sum(1 for site in sites if 1 <= site.get((name + '-stock-levels') / site.get((name + '-quantity_used').lower())) < 2) / site_count),
        'two_three': '{:.2%}'.format(sum(1 for site in sites if 2 <= site.get((name + '-stock-levels') / site.get((name + '-quantity_used').lower())) < 3) / site_count),
        'less-than-week': '{:.2%}'.format(sum(1 for site in sites if 3 <= site.get((name + '-stock-levels') / site.get((name + '-quantity_used').lower())) < 7) / site_count),
        'more-than-week': '{:.2%}'.format(sum(1 for site in sites if 7 <= site.get((name + '-stock-levels') / site.get((name + '-quantity_used').lower()))) / site_count),
    }

    rags = ('under_one', 'one_two', 'two_three', 'less-than-week','more-than-week')
    max_item = 'under_one'
    for prop in rags:
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
    rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
    sorted_items = sorted(items, key=lambda x: [x[r] for r in rags])
    print([i['highlight'] for i in sorted_items], file=sys.stderr)
    return_items = []
    for r in rags:
        print(r, file=sys.stderr)
        rag_items = [item for item in sorted_items if item['highlight'] == r]
        return_items.append(rag_items)

    return return_items
