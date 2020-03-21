#!/usr/bin/env bash

# Exit on error
set -euxo pipefail

DATE=$(date +"%Y%m%d%H%M")
curl -X POST -d "name=David&company=Carboni.io&submitted-at=$DATE" https://europe-west2-loans-271821.cloudfunctions.net/form
