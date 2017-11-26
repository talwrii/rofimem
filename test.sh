#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
here="$(dirname BASH_SOURCE[0])"

cd "$here"

rm -rf venv
virtualenv venv
venv/bin/pip install .
venv/bin/rofimem --help > /dev/null

rm -rf venv
virtualenv -p python3 venv
venv/bin/pip install .
venv/bin/rofimem --help > /dev/null
