FROM certbot/certbot

WORKDIR /app
COPY . /app

ENTRYPOINT ["./bin/run.sh"]
CMD ["--help"]