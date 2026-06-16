#!/bin/bash

if [ ! -f "signing_key.pem" ]; then
    echo "signing_key.pem does not exist. Generating..."
    openssl genrsa -out signing_key.pem 4096
fi

# jag bashar mitt huve i väggen snart
source .venv/bin/activate
gunicorn -w 1 --timeout 60 -b 0.0.0.0:5000 "koseki:run_prod()"
