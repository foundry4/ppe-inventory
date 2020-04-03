#!/usr/bin/env bash

# Exit on error
set -euxo pipefail

# Check input files
EXIT=no
if [ ! -f "account.txt" ]; then
    echo "Please create a file called account.txt containing your GCP login email."
    EXIT=yes
fi
if [ ! -f "project_id.txt" ]; then
    echo "Please create a file called project_id.txt containing your GCP project ID."
    EXIT=yes
fi
if [ ! -f "sheet-id.txt" ]; then
    echo "Please create a file called sheet-id.txt containing the ID of your Google sheet."
    EXIT=yes
fi
if [ ! -f "worksheet-name.txt" ]; then
    echo "Please create a file called worksheet-name.txt containing the name of a worksheet in your Google sheet."
    EXIT=yes
fi
if [ ! "$EXIT" = "no" ]; then
    exit 1
fi

# Setup

base=$PWD

account=$(cat account.txt)
project_id=$(cat project_id.txt)
gcloud config set account $account
gcloud config set project $project_id

form_page=$(cat form_page.txt)
success_page=$(cat success_page.txt)
error_page=$(cat error_page.txt)
sheet_id=$(cat sheet-id.txt)
worksheet_name=$(cat worksheet-name.txt)

# Enable APIs

  gcloud services enable cloudfunctions.googleapis.com

  gcloud services enable sheets.googleapis.com


# Static content
#gsutil mb gs://ppe-inventory
gsutil rsync -r static gs://ppe-inventory
gsutil iam ch allUsers:objectViewer gs://ppe-inventory
#gsutil web set -m index.html -e 404.html gs://www.example.com


# Web form function

cd $base/form
env_vars="--set-env-vars=DOMAIN=europe-west2-${project_id}.cloudfunctions.net"
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"

gcloud functions deploy form --runtime=python37 --trigger-http ${env_vars} ${options}


# Registration function

cd $base/register
env_vars="--set-env-vars=DOMAIN=europe-west2-${project_id}.cloudfunctions.net"
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"

gcloud functions deploy register --runtime=python37 --trigger-http ${env_vars} ${options}


# Data update function

cd $base/update
env_vars="--set-env-vars=DOMAIN=europe-west2-${project_id}.cloudfunctions.net"
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"

gcloud functions deploy form --runtime=nodejs10 --trigger-http ${env_vars} ${options}


# Google sheets function
# NB: limited to 1 instance to avoid race conditions when updating the spreadsheet

cd $base/sheets
concurrency=" --max-instances=1"
env_vars="--set-env-vars=SHEET_ID=$sheet_id,WORKSHEET_NAME=$worksheet_name"
options="--region=europe-west2 --memory=256MB --allow-unauthenticated"

gcloud functions deploy inventory --runtime=python37 --trigger-http ${concurrency} ${env_vars} ${options}
gcloud functions deploy sheets --runtime=python37 --trigger-topic=form-submissions ${concurrency} ${env_vars} ${options}

cd $base

# Report back

# echo "*** Please grant edit permissions on the spreadsheet to ${service_account} (https://docs.google.com/spreadsheets/d/${sheet_id})"
echo "*** Please grant edit permissions on the spreadsheet to ${project_id}@appspot.gserviceaccount.com (https://docs.google.com/spreadsheets/d/${sheet_id})"
gcloud functions describe form --region=europe-west2 | grep url
