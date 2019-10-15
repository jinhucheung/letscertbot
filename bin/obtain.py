#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Config, Logger, Utils

certbot_email = Config.get('base', 'certbot_email')
manual_hook_path = os.path.sep.join([root_path, 'bin', 'manual_hook.py'])

certbot_cmd_template = '''
    certbot certonly \
    --email %(email)s \
    --manual-public-ip-logging-ok \
    --agree-tos \
    --preferred-challenges dns \
    --server https://acme-v02.api.letsencrypt.org/directory \
    --manual \
    --manual-auth-hook "python %(manual_hook_path)s --auth" \
    --manual-cleanup-hook "python %(manual_hook_path)s --cleanup" \
    %(domains)s
'''

def run(args):
    domains = map(lambda domain: '-d ' + domain, args.domains)
    domains = ' '.join(domains)

    Logger.info('obtain domains: ' + domains)

    certbot_cmd = certbot_cmd_template % {
        'email': Config.get('base', 'certbot_email'),
        'manual_hook_path': manual_hook_path,
        'domains': domains
    }

    Logger.info('certbot obtain: ' + certbot_cmd)

    os.system(certbot_cmd)

def main():
    parser = argparse.ArgumentParser(description='example: python %s -d domain.com *.domain.com' % os.path.basename(__file__))

    parser.add_argument('-d', '--domains', help='domain list', required=True, nargs='+')

    args = parser.parse_args()

    Logger.info(args)

    run(args)

if __name__ == '__main__':
    main()

