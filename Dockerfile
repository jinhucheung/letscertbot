FROM certbot/certbot

WORKDIR /app
COPY . /app

ENTRYPOINT ["./bin/entrypoint.sh"]