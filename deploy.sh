#!/usr/bin/env bash


# Exit on error

set -euxo pipefail


# Check input files

EXIT=no
if [ ! -f "exclude/account.txt" ]; then
    echo "Please create a file called exclude/account.txt containing your GCP login email."
    EXIT=yes
fi
if [ ! -f "exclude/project_id.txt" ]; then
    echo "Please create a file called exclude/project_id.txt containing your GCP project ID."
    EXIT=yes
fi
if [ ! -f "exclude/sheet-id.txt" ]; then
    echo "Please create a file called exclude/sheet-id.txt containing the ID of your Google sheet."
    EXIT=yes
fi
if [ ! -f "exclude/worksheet-name.txt" ]; then
    echo "Please create a file called exclude/worksheet-name.txt containing the name of a worksheet in your Google sheet."
    EXIT=yes
fi
if [ ! "$EXIT" = "no" ]; then
    exit 1
fi


# Setup

base=$PWD

# Google Cloud login email
account=$(cat exclude/account.txt)

# GCP Projeect ID
project_id=$(cat exclude/project_id.txt)

# The ID of the Google spreadsheet to use for output
sheet_id=$(cat exclude/sheet-id.txt)

# The name of the worksheet in the spreadsheet to use for output
worksheet_name=$(cat exclude/worksheet-name.txt)

gcloud config set account $account
gcloud config set project $project_id

# Variables
domain=europe-west2-${project_id}.cloudfunctions.net
community_sheet_id=$sheet_id #?

# Enable APIs

gcloud services enable cloudfunctions.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com


# Pubsub

gcloud pubsub topics describe form-submissions || \
gcloud pubsub topics create form-submissions


# Static content

bucket_name=${project_id}-static
gsutil ls -b gs://${bucket_name} || \
gsutil mb gs://${bucket_name}
gsutil rsync -r static gs://${bucket_name}
gsutil iam ch allUsers:objectViewer gs://${bucket_name}


# Web form function

cd $base/form
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"
gcloud functions deploy form --runtime=python37 --trigger-http --set-env-vars=PROJECT_ID=${project_id},DOMAIN=${domain},BUCKET_NAME=${bucket_name} ${options} &


# Registration function

cd $base/register
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"
gcloud functions deploy register --runtime=python37 --trigger-http --set-env-vars=DOMAIN=${domain},BUCKET_NAME=${bucket_name} ${options} &


# Google sheets function
# NB: limited to 1 instance to avoid race conditions when updating the spreadsheet

cd $base/sheets
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"
gcloud functions deploy sheets --runtime=python37 --trigger-topic=form-submissions --set-env-vars=COMMUNITY_SHEET_ID=${community_sheet_id},SHEET_ID=${sheet_id},WORKSHEET_NAME=${worksheet_name},BUCKET_NAME=${bucket_name} ${options} --max-instances=1 &


# Barts (deprecated)

cd $base/barts
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"
gcloud functions deploy barts --runtime=python37 --trigger-http --set-env-vars=PROJECT_ID=${project_id},DOMAIN=${domain},BUCKET_NAME=${bucket_name} ${options} &


# Dashboard

cd $base/dashboard
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"
gcloud functions deploy dashboard --runtime=python37 --trigger-http --set-env-vars=PROJECT_ID=${project_id},DOMAIN=${domain} ${options} &


# Search

cd $base/search
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"
gcloud functions deploy search --runtime=python37 --trigger-http --set-env-vars=PROJECT_ID=${project_id},DOMAIN=${domain},BUCKET_NAME=${bucket_name} ${options} &


wait


# Portal

cd $base/server
options="--platform managed --region europe-west1  --allow-unauthenticated"
gcloud builds submit --tag gcr.io/${project_id}/${project_id}
gcloud run deploy ${project_id} --image gcr.io/${project_id}/${project_id} --set-env-vars=USERNAME=ppe,PASSWORD=password ${options}


# Report back

cd $base
echo "** Please grant edit permissions on the spreadsheet to ${project_id}@appspot.gserviceaccount.com (https://docs.google.com/spreadsheets/d/${sheet_id})"
echo "** Please ensure you've set up your Datastore database in the GCP console."
