#!/bin/sh

certbot certonly \
--email hi.jinhu.zhang@gmail.com \
--manual-public-ip-logging-ok \
--agree-tos \
--preferred-challenges dns \
--server https://acme-v02.api.letsencrypt.org/directory \
--manual \
--manual-auth-hook 'python manual_hook.py --auth' \
--manual-cleanup-hook 'python manual_hook.py --cleanup' \
-d *.de.yourdomain.com \
-d de.yourdomain.com