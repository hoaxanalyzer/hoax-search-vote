#!/usr/bin/env bash
export HTTP_PROXY="http://167.205.22.102:8800"
export HTTPS_PROXY="http://167.205.22.102:8800"

gunicorn --bind 0.0.0.0:8080 --workers=3 --timeout 500 wsgi > /var/www/hoaxa/logs/gunicorn-access.log
