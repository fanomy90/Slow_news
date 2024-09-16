#!/bin/bash

# Путь к SSL сертификатам
CERT_PATH="/etc/letsencrypt/live/slow-news.sytes.net/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/slow-news.sytes.net/privkey.pem"

# Проверка существования сертификатов
if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
    echo "Сертификаты не найдены. Генерация новых сертификатов..."
    # certbot certonly --webroot --webroot-path=/yt/static --email fanomy90@gmail.com --agree-tos --no-eff-email -d slow-news.sytes.net
    certbot certonly --webroot --webroot-path=/yt/static --email fanomy90@gmail.com --agree-tos --no-eff-email --non-interactive -d slow-news.sytes.net

    nginx -s reload
else
    # Проверка актуальности сертификатов
    echo "Проверка актуальности сертификатов..."
    certbot renew --dry-run
    if [ $? -eq 0 ]; then
        echo "Сертификаты актуальны."
    else
        echo "Обновление сертификатов..."
        certbot renew
        nginx -s reload
    fi
fi