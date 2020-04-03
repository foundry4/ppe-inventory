from flask import request, make_response, redirect
import os


def register(request):

    site = request.args.get('site')
    code = request.args.get('code')
 
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain=os.getenv('DOMAIN')
    response = make_response(redirect(f'https://{domain}/form'))
    print(response.location)

    if site and code:
        print(f"Setting cookie site={site}, code={code}")
        response.set_cookie('site', site, expires=30*86400)
        response.set_cookie('code', code, expires=30*86400)
        #response.set_cookie('code', code, secure=True, httponly=True, expires=30*86400)
    else:
        print("Not setting registration cookie")

    return response
