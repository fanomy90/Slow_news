#!/bin/sh

# Бесконечный цикл, выполняющий проверку сертификатов каждые 1 день (86400 секунд)
# echo "Запуск cert_update.sh" >> /tmp/debug.log
echo "Запуск cert_update.sh"
while true; do
    echo "Запуск cert_check.sh"
    /usr/local/bin/cert_check.sh  # Запуск скрипта проверки сертификатов
    
    # # Проверка и перезагрузка Nginx, если сертификаты были обновлены
    # if [ -f /tmp/renewed ]; then
    #     /usr/local/bin/nginx-reload.sh
    #     rm /tmp/renewed  # Удаление флага обновления
    # fi
    
    sleep 86400  # 1 день в секундах
    # sleep 604800  # 7 дней в секундах
done