#!/bin/bash

gunicorn -w 1 --timeout 5 -b 127.0.0.1:5000 "koseki:run_koseki(False)"
