FROM certbot/certbot

RUN apk update && apk add openssh sshpass man man-pages

WORKDIR /app
COPY . /app

ENTRYPOINT ["./bin/entrypoint.sh"]