FROM nginx:latest
# RUN rm /etc/nginx/conf.d/default.conf
# COPY nginx.conf /etc/nginx/conf.d
# COPY proxy_params /etc/nginx

# COPY ./tmp/nginx-http.conf /etc/nginx/conf.d/nginx-http.conf
# COPY ./tmp/nginx-https.conf /etc/nginx/conf.d/nginx-https.conf
# COPY ./tmp/nginx-ssl.conf /etc/nginx/conf.d/nginx-ssl.conf

# Копируем конфигурацию Nginx в контейнер
# COPY ./nginx.conf /etc/nginx/nginx.conf

# Копируем параметры прокси (если нужно)
# COPY ./proxy_params /etc/nginx/proxy_params

# Убедитесь, что директивы для Certbot будут корректно работать
RUN mkdir -p /var/www/html

# Стандартная команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]