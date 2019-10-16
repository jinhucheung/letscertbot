#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Config, Logger

manual_hook_path = os.path.sep.join([root_path, 'bin', 'manual_hook.py'])
deploy_hook_path = os.path.sep.join([root_path, 'bin', 'deploy_hook.py'])

certbot_cmd_template = '''
    certbot renew \
    -n \
    --agree-tos \
    --manual \
    --manual-public-ip-logging-ok \
    --manual-auth-hook "python %(manual_hook_path)s --auth" \
    --manual-cleanup-hook "python %(manual_hook_path)s --cleanup" \
    %(deploy_hook)s \
    %(cert_names)s \
    %(force_renewal)s
'''

def run(args):
    cert_names = map(lambda domain: '--cert-name ' + domain, args.certs)
    cert_names = ' '.join(cert_names)

    Logger.info('obtain cert_names: ' + cert_names)

    force_renewal = '--force-renewal' if args.force else ''

    deploy_hook = '--deploy-hook "python ' + deploy_hook_path + '"' if Config['deploy']['enable'] else ''

    certbot_cmd = certbot_cmd_template % {
        'manual_hook_path': manual_hook_path,
        'deploy_hook': deploy_hook,
        'cert_names': cert_names,
        'force_renewal': force_renewal
    }

    Logger.info('certbot renew: ' + certbot_cmd)

    os.system(certbot_cmd)

def main():
    parser = argparse.ArgumentParser(description='example: python %s' % os.path.basename(__file__))

    parser.add_argument('-f', '--force', help='force renewal', default=False, action='store_true')
    parser.add_argument('-c', '--certs', help='cert list, e.g. domain.com', default=[], nargs='*')

    args = parser.parse_args()

    Logger.info(args)

    run(args)

if __name__ == '__main__':
    main()