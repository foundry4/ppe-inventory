from google.cloud import datastore


def get_sites():
    client = datastore.Client()
    query = client.query(kind='Site')
    sites = list(query.fetch())

    return [site for site in sites if site.get('acute') != 'yes']


def get_site(name, code):
    client = datastore.Client()
    print(f"Getting site: {name}/{code}")
    key = client.key('Site', name)
    site = client.get(key)
    if site and site.get('code') == code:
        return site

    print(f"No site detected in db: {name}/{code}")
    return None
