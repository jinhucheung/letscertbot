#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Config, Logger

manual_path = os.path.sep.join([root_path, 'bin', 'manual.py'])
deploy_path = os.path.sep.join([root_path, 'bin', 'deploy.py'])

certbot_cmd_template = '''
    certbot certonly \
    -n \
    --email %(email)s \
    --agree-tos \
    %(cert_name)s \
    %(force_renewal)s \
    --preferred-challenges dns \
    --server https://acme-v02.api.letsencrypt.org/directory \
    --manual \
    --manual-public-ip-logging-ok \
    --manual-auth-hook "python %(manual_path)s --auth" \
    --manual-cleanup-hook "python %(manual_path)s --cleanup" \
    %(deploy_hook)s \
    %(domains)s
'''

def run(args):
    domains = map(lambda domain: '-d ' + domain, args.domains)
    domains = ' '.join(domains)

    Logger.info('obtain domains: ' + domains)

    deploy_hook = '--deploy-hook "python ' + deploy_path + '"' if Config['deploy']['enable'] else ''
    cert_name = '--cert-name ' + args.cert if args.cert else ''
    force_renewal = '--force-renewal' if args.force else ''

    certbot_cmd = certbot_cmd_template % {
        'email': Config['base']['email'],
        'cert_name': cert_name,
        'force_renewal': force_renewal,
        'manual_path': manual_path,
        'deploy_hook': deploy_hook,
        'domains': domains
    }

    Logger.info('certbot obtain: ' + certbot_cmd)

    os.system(certbot_cmd)

def main():
    parser = argparse.ArgumentParser(description='example: python %s -d domain.com *.domain.com' % os.path.basename(__file__))

    parser.add_argument('-d', '--domains', help='domain list', required=True, nargs='+')
    parser.add_argument('-c', '--cert', help='cert name, e.g. domain.com')
    parser.add_argument('-f', '--force', help='force renewal', default=False, action='store_true')

    args = parser.parse_args()

    Logger.info(args)

    run(args)

if __name__ == '__main__':
    main()

