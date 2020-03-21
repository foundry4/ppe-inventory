#!/usr/bin/env bash

# Exit on error
set -euxo pipefail

DATE=$(date +"%Y%m%d%H%M")
curl -X POST -d "test=David&timestamp=$DATE" https://europe-west2-spreadform.cloudfunctions.net/form
