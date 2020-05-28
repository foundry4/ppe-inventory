from flask import request, make_response, redirect, flash
import os


def register(request):

    site = request.args.get('site')
    code = request.args.get('code')
 
    # Construct a full URL to redirect to
    # otherwise we seem to end up on http
    domain=os.getenv('DOMAIN')
    response = make_response(redirect(f'https://{domain}/form?site={site}&code={code}'))

    print(response)

    print(f"Redirecting to {response.location}")
    # flash(f'You have been redirected from an old link. Please use https://{portal}/sites/{code}')
    return response
