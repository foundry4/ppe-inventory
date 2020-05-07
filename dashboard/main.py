import datetime
from flask import make_response, render_template
from db import get_sites, get_site
import sys
import pandas as pd
import numpy as np


def dashboard(request):
    return 'This function is currently not available.'
    response = render_dashboard()
    return response


def render_dashboard():
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
    df = get_dataframe(sites, item_names)
    items = get_ppe_items(item_names, df)
    sorted_items = sort_ppe_items(items)
    print(sorted_items, file=sys.stderr)
    response = make_response(render_template(template,
                                             item_count=len(sorted_items),
                                             items=sorted_items,
                                             site_count = len(sites),
                                             updated_site_count = len(updated_sites),
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))
    return response


def get_dataframe(sites, item_names):
    df = pd.DataFrame(columns=['name', 'item', 'stock-level', 'quantity_used'])
    i = 0
    for site in sites:
        for item in item_names:
            df.loc[i] = site.get('site'), item, site.get(item + '-stock-levels'), site.get(item + '-quantity_used')
            i += 1
    df[['stock-level', 'quantity_used']] = df[['stock-level', 'quantity_used']].apply(pd.to_numeric)
    # df.fillna(0, inplace=True)
    df['weekly'] = df.apply(
        lambda x: 0 if x['stock-level'] == 0 else np.nan if x['quantity_used'] == 0 else x['stock-level'] / x[
            'quantity_used'], axis=1)
    df.dropna(inplace=True)
    df['rag'] = \
        df['weekly'].apply(
            lambda x: 'under_one' if x < 1
                else 'one_two' if x < 2
                else 'two_three' if x < 3
                else 'less-than-week' if x < 7
                else 'more-than-week')
    return df


def get_ppe_items(item_names, df):
    for name in item_names:
        item = get_ppe_item(item_names, name, df)
        yield item


def get_ppe_item(item_names, name, df):
    if len(df[(df['item'] == name)]) > 0:
        ppe_item = {
            'name': name,
            'display_name' : item_names[name],
            'under_one': '{:.0%}'.format(
                len(df[(df['item'] == name) & (df['rag'] == 'under_one')]) / len(df[(df['item'] == name)])),
            'one_two': '{:.0%}'.format(
                len(df[(df['item'] == name) & (df['rag'] == 'one_two')]) / len(df[(df['item'] == name)])),
            'two_three': '{:.0%}'.format(
                len(df[(df['item'] == name) & (df['rag'] == 'two_three')]) / len(df[(df['item'] == name)])),
            'less-than-week': '{:.0%}'.format(
                len(df[(df['item'] == name) & (df['rag'] == 'less-than-week')]) / len(df[(df['item'] == name)])),
            'more-than-week': '{:.0%}'.format(
                len(df[(df['item'] == name) & (df['rag'] == 'more-than-week')]) / len(df[(df['item'] == name)])),
        }

        rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
        max_item = 'under_one'
        for prop in rags:
            if ppe_item[prop] > ppe_item[max_item]:
                max_item = prop
        ppe_item['highlight'] = max_item
        return ppe_item

    # return empty item if no values avialable
    return {
        'name': name,
        'display_name': item_names[name],
        'under_one': '{:.0%}'.format(0),
        'one_two': '{:.0%}'.format(0),
        'two_three': '{:.0%}'.format(0),
        'less-than-week': '{:.0%}'.format(0),
        'more-than-week': '{:.0%}'.format(0),
        'highlight': 'under_one'
    }


def sort_ppe_items(items):
    rags = ('under_one', 'one_two', 'two_three', 'less-than-week', 'more-than-week')
    sorted_items = sorted(items, key=lambda x: [x[r] for r in rags])
    # print([i['highlight'] for i in sorted_items], file=sys.stderr)
    return_items = []
    for r in rags:
        print(r, file=sys.stderr)
        for item in sorted_items:
            if item['highlight'] == r:
                return_items.append(item)

    return return_items
