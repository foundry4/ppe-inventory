import datetime
from flask import make_response, render_template
from db import get_sites, get_site, get_ppe_items_from_db
import sys


def dashboard(request):
    # return 'This function is currently not available.'
    response = render_dashboard()
    return response


def render_dashboard():
    sites = get_sites()

    updated_sites = [site.get('last_update') for site in sites if
                     site.get('last_update') and site.get('last_update').date() >= (
                             datetime.date.today() - datetime.timedelta(days=7))]

    print(f"{len(updated_sites)} of {len(sites)} sites have been updated.")

    template = 'dashboard.html'

    item_names = get_item_names()

    print(f"Rendering {template}")
    db_items = get_ppe_items_from_db()
    ppe_items = get_ppe_items(item_names, db_items)
    sorted_items = sort_ppe_items(ppe_items)
    print(sorted_items, file=sys.stderr)
    response = make_response(render_template(template,
                                             item_count=len(sorted_items),
                                             items=sorted_items,
                                             site_count=len(sites),
                                             updated_site_count=len(updated_sites),
                                             currentTime=datetime.datetime.now().strftime('%H:%M %d %B %y'),
                                             assets='https://storage.googleapis.com/ppe-inventory',
                                             data={}
                                             ))
    return response


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
        print(r, file=sys.stderr)
        for item in sorted_items:
            if item['highlight'] == r:
                return_items.append(item)

    return return_items
