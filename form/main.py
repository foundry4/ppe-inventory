from flask import request, make_response, redirect, render_template, abort


def form(request):

    site = request.cookies.get('site')
    code = request.cookies.get('code')

    template = 'ppe-inventory.html' if site else 'ppe-error.html'

    form = make_response(render_template(template, 
        site=site,
        assets='https://storage.googleapis.com/ppe-inventory',
        data={
            }
        ))
    return form
