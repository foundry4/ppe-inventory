from flask import request, make_response, redirect, render_template, abort
import json
import os
import requests


def ppe_inventory_form(request):

    site = request.cookies.get('site')
    if not site:
        abort(400)

    form = make_response(render_template('ppe-inventory.html', 
        data={'site': site}
        ))
    return form
