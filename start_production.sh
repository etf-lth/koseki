#!/bin/bash

python3.9 -m gunicorn -w 1 --timeout 5 -b 127.0.0.1:5000 "koseki:run_prod()"
