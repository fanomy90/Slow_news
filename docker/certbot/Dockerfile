FROM certbot/certbot:latest
RUN apk add --no-cache docker-cli
RUN mkdir -p /var/log/certbot
COPY ./cert_init.sh /usr/local/bin/cert_init.sh
RUN chmod +x /usr/local/bin/cert_init.sh\
    && ls -l /usr/local/bin
CMD ["/usr/local/bin/cert_init.sh"]