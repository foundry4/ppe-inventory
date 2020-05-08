from flask import request, make_response, redirect, flash
import datetime
import os


def register(request):

    site = request.args.get('site')
    code = request.args.get('code')
 
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain=os.getenv('DOMAIN')
    # response = make_response(redirect(f'https://{domain}/form'))

    portal = os.getenv('PORTAL')
    response = make_response(redirect(f'https://{portal}/forms/{code}'))
    print(response)

    if site and code:
        print(f"Setting cookie site={site}, code={code}")
        expire_date = datetime.datetime.now() + datetime.timedelta(days=90)
        response.set_cookie('site', site, expires=expire_date, secure=True)
        response.set_cookie('code', code, expires=expire_date, secure=True)
    else:
        print("Not setting registration cookie")

    print(f"Redirecting to {response.location}")
    # flash(f'You have been redirected from an old link. Please use https://{portal}/sites/{code}')
    return response
