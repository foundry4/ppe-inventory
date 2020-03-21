#!/usr/bin/env bash

# Exit on error
set -euxo pipefail

curl -X POST -d "message1=Hello&message2=world" https://europe-west2-spreadform.cloudfunctions.net/form

