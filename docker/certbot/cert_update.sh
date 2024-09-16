#!/bin/bash

# Бесконечный цикл, выполняющий проверку сертификатов каждые 7 дней (604800 секунд)
while true; do
    /usr/local/bin/cert_check.sh  # Запуск скрипта проверки сертификатов
    sleep 604800  # 7 дней в секундах
done