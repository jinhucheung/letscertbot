#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import getopt
import argparse

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

# load api, lib
sys.path.append(root_path)
import api
from lib import Config, Logger, Utils

def auth(type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')
        if 'CERTBOT_VALIDATION' not in os.environ:
            raise Exception('Environment variable CERTBOT_VALIDATION is empty.')

        certbot_domain = os.environ['CERTBOT_DOMAIN']
        certbot_validation = os.environ['CERTBOT_VALIDATION']

        Logger.info('manual_hook#auth: Start to setting dns')
        Logger.info('manual_hook#auth certbot_domain: ' + certbot_domain)
        Logger.info('manual_hook#auth certbot_validation: ' + certbot_validation)

        maindomain, acme_challenge = __extract_maindomain_and_challenge(certbot_domain)

        client = __get_api_client(type)
        client.add_domain_record(maindomain, acme_challenge, certbot_validation)

        Logger.info('manual_hook#auth: sleep 10 secs')
        time.sleep(10)

        Logger.info('manual_hook#auth: Success.')
    except Exception as e:
        Logger.error('manual_hook#auth raise Exception:' + str(e))
        sys.exit()

def cleanup(type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')

        certbot_domain = os.environ['CERTBOT_DUtlsOMAIN']

        Logger.info('manual_hook#cleanup: Start to cleanup dns')
        Logger.info('manual_hook#cleanup: ' + certbot_domain)

        maindomain, acme_challenge = __extract_maindomain_and_challenge(certbot_domain)

        client = __get_api_client(type)
        client.delete_domain_record(maindomain, acme_challenge)

        Logger.info('manual_hook#cleanup: sleep 10 secs')
        time.sleep(10)

        Logger.info('manual_hook#cleanup: Success.')
    except Exception as e:
        Logger.error('manual_hook#cleanup raise Exception:' + str(e))
        sys.exit()

def __get_api_client(type = 'aliyun'):
    try:
        switch = {
            'aliyun': __get_alidns_client
        }
        return switch[type]()
    except KeyError as e:
        Logger.error('manual_hook#get_api raise KeyError: ' + str(e))
        raise SystemExit(e)

def __get_alidns_client():
    access_key_id = Config.get('aliyun', 'access_key_id')
    access_key_secret = Config.get('aliyun', 'access_key_secret')

    return api.AliDns(access_key_id, access_key_secret)

def __extract_maindomain_and_challenge(domain):
    sudomain, maindomain = Utils.extract_domain(domain)

    acme_challenge = Config.get('base', 'acme_challenge')

    if sudomain:
        acme_challenge += '.' + sudomain

    Logger.info('manual_hook maindomain: ' + maindomain)
    Logger.info('manual_hook acme_challenge: ' + acme_challenge)

    return (maindomain, acme_challenge)

def main():
    parser = argparse.ArgumentParser(description='example: python %s --auth --api aliyun' % os.path.basename(__file__))

    parser.add_argument('-a', '--auth', help='auth hook', action='store_true')
    parser.add_argument('-c', '--cleanup', help='auth hook', action='store_true')
    parser.add_argument('--api', help='api type, default: aliyun', default='aliyun')

    args = parser.parse_args()

    Logger.info(args)

    if args.auth:
        auth(args.api)
    elif args.cleanup:
        cleanup(args.api)

if __name__ == '__main__':
    main()