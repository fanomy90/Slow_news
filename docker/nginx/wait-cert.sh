#!/bin/bash

while [ ! -f /etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem ]; do
    echo "Waiting for certbot to generate certificates..."
    sleep 5
done
nginx -g 'daemon off;'