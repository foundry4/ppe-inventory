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

# Service account - less privilege, but more complex

#service_account_name=functions
#gcloud iam service-accounts describe ${service_account_name}@${project_id}.iam.gserviceaccount.com || \
#gcloud iam service-accounts create ${service_account_name} --display-name "Funcitons" --description "Service accout for spreadform functions"
#service_account=${service_account_name}@${project_id}.iam.gserviceaccount.com

# Pubsub topic

gcloud pubsub topics describe form-submissions || \
gcloud pubsub topics create form-submissions
#echo "{
#     \"bindings\": [
#       {
#         \"role\": \"roles/pubsub.editor\",
#         \"members\": [
#           \"serviceAccount:${service_account}\"
#         ]
#       }
#     ]
#   }" > form-submissions.policy.json
# Answer yes to the prompt to update the policy:
#printf 'y\n' | gcloud pubsub topics set-iam-policy projects/spreadform/topics/form-submissions form-submissions.policy.json
#rm form-submissions.policy.json 

# Google sheets function
# NB: limited to 1 instance to avoid race conditions when updating the spreadsheet

cd $base/sheets
concurrency=" --max-instances=1"
env_vars="--set-env-vars=SHEET_ID=$sheet_id,WORKSHEET_NAME=$worksheet_name"
options="--region=europe-west2 --memory=256MB --trigger-topic=form-submissions --allow-unauthenticated"

gcloud functions deploy sheets --runtime=python37 ${concurrency} ${env_vars} ${options} #--service-account=${service_account}

cd $base

# Web form function

cd $base/form
env_vars="--set-env-vars=FORM_PAGE=$form_page,SUCCESS_PAGE=$success_page,ERROR_PAGE=$error_page"
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"

gcloud functions deploy form --runtime=nodejs10 ${env_vars} ${options} #--service-account=${service_account}

cd $base

# Report back

# echo "*** Please grant edit permissions on the spreadsheet to ${service_account} (https://docs.google.com/spreadsheets/d/${sheet_id})"
echo "*** Please grant edit permissions on the spreadsheet to ${project_id}@appspot.gserviceaccount.com (https://docs.google.com/spreadsheets/d/${sheet_id})"
gcloud functions describe form --region=europe-west2 | grep url
