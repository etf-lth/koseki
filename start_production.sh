#!/bin/bash

if [ ! -f "signing_key.pem" ]; then
    echo "signing_key.pem does not exist. Generating..."
    openssl genrsa -out signing_key.pem 4096
fi

gunicorn -w 1 --timeout 60 -b 127.0.0.1:5000 "koseki:run_prod()"
