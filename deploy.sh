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

sheet_id=$(cat sheet-id.txt)
worksheet_name=$(cat worksheet-name.txt)

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

# Pubsub subscriptions

gcloud pubsub subscriptions describe sheets || \
gcloud pubsub subscriptions create sheets --topic form-submissions

# Web form

cd $base/form
env_vars="--set-env-vars=[SHEET_ID=$sheet_id,WORKSHEET_NAME=$worksheet_name]"
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"

gcloud functions deploy form --runtime=nodejs10 ${env_vars} ${options} --entry-point=form #--service-account=${service_account}

# Report back

echo "Please grant edit permissions on the spreadsheet to ${project_id}@appspot.gserviceaccount.com (https://docs.google.com/spreadsheets/d/${sheet_id})"