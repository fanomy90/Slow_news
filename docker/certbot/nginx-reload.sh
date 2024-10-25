#!/bin/sh

if [ -f /tmp/renewed ]; then
    echo "Обновленные сертификаты обнаружены. Перезагрузка Nginx..."
    docker exec nginx nginx -s reload
    # docker-compose restart nginx
    rm /tmp/renewed
fi