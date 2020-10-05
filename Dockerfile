FROM certbot/certbot

RUN apk update && apk add openssh sshpass mandoc man-pages

WORKDIR /app
COPY . /app

ENTRYPOINT ["./bin/entrypoint.sh"]