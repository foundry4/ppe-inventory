FROM python:alpine

# Git and dependencies for psycopg2
#RUN apk update && apk add git postgresql-dev gcc python3-dev musl-dev

WORKDIR /ppe-inventory

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

USER 1000

# This is isn't recommended, but it's enough to run a low-traffic wiki
# NB Flask defaults to looking for app.py
ENTRYPOINT python app.py
