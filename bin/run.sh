#!/bin/sh

certbot certonly \
--email hi.jinhu.zhang@gmail.com \
--agree-tos \
--preferred-challenges dns \
--server https://acme-v02.api.letsencrypt.org/directory \
--manual \
--manual-auth-hook ./authenticator.sh \
--manual-cleanup-hook ./cleanup.sh \
-d *.de.yourdomain.com \
-d de.yourdomain.com