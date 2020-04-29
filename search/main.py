from flask import request, make_response, redirect, render_template, abort, flash, url_for
from google.cloud import datastore
from google.cloud import pubsub_v1
import datetime
import json
import os

currentTime = datetime.datetime.now()


def search(request):
    print(request)

    return render_template('hello.html', places=["Hospital 1", "Hospital 2"])
