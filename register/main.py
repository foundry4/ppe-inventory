from flask import request, make_response, redirect
import os


def register(request):

    site = request.args.get('site')
    code = request.args.get('code')
 
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain=os.getenv('DOMAIN')
    response = make_response(redirect(f'https://{domain}/form'))

    if site and code:
        print(f"Setting cookie site={site}, code={code}")
        response.set_cookie('site', value=site)
        response.set_cookie('code', value=code)
        # response.set_cookie('site', value=site, domain=domain, expires=30*86400, secure=True, httponly=True)
        # response.set_cookie('code', value=code, domain=domain, expires=30*86400, secure=True, httponly=True)
        #response.set_cookie('code', code, secure=True, httponly=True, expires=30*86400)
    else:
        print("Not setting registration cookie")

    print(f"Redirecting to {response.location}")
    return response
