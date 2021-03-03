#!/bin/bash

gunicorn -w 1 --timeout 60 -b 127.0.0.1:5000 "koseki:run_prod()"
