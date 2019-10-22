#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import argparse
import string
import random

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
import api
from lib import Config, Logger, Utils

def auth(api_type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')
        if 'CERTBOT_VALIDATION' not in os.environ:
            raise Exception('Environment variable CERTBOT_VALIDATION is empty.')

        certbot_domain = os.environ['CERTBOT_DOMAIN']
        certbot_validation = os.environ['CERTBOT_VALIDATION']

        Logger.info('manual#auth: Start to setting dns')
        Logger.info('manual#auth certbot_domain: ' + certbot_domain)
        Logger.info('manual#auth certbot_validation: ' + certbot_validation)

        maindomain, acme_challenge = __extract_maindomain_and_challenge(certbot_domain)

        client = __get_api_client(api_type)
        client.add_domain_record(maindomain, acme_challenge, certbot_validation)

        Logger.info('manual#auth: sleep 10 seconds')
        time.sleep(10)

        Logger.info('manual#auth: Success.')
    except Exception as e:
        Logger.error('manual#auth raise Exception:' + str(e))
        sys.exit()

def cleanup(api_type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')

        certbot_domain = os.environ['CERTBOT_DOMAIN']

        Logger.info('manual#cleanup: Start to cleanup dns')
        Logger.info('manual#cleanup: ' + certbot_domain)

        maindomain, acme_challenge = __extract_maindomain_and_challenge(certbot_domain)

        client = __get_api_client(api_type)
        client.delete_domain_record(maindomain, acme_challenge)

        Logger.info('manual#cleanup: sleep 10 seconds')
        time.sleep(10)

        Logger.info('manual#cleanup: Success.')
    except Exception as e:
        Logger.error('manual#cleanup raise Exception:' + str(e))
        sys.exit()

def test(domain, api_type = 'aliyun'):
    try:
        print('start to test ' + domain + ' in DNS ' + api_type + ' API')

        client = __get_api_client(api_type)
        maindomain, acme_challenge = __extract_maindomain_and_challenge(domain)
        validation = ''.join(random.sample(string.ascii_letters + string.digits, 16))

        print('add TXT record(domain=' + maindomain + ', rr=' + acme_challenge + ', value=' + validation + ') to ' + api_type + ' DNS')
        client.add_domain_record(maindomain, acme_challenge, validation)
        print('added TXT record')

        print('waiting 10 seconds...')
        time.sleep(10)

        print('remove above TXT record')
        client.delete_domain_record(maindomain, acme_challenge)
        print('removed TXT record')

        print('tested ' + domain + ' in DNS ' + api_type + ' API')
    except Exception as e:
        Logger.error('test raise Exception:' + str(e))
        sys.exit()

def __get_api_client(api_type = 'aliyun'):
    try:
        switch = {
            'aliyun': __get_aliyun_client
        }
        return switch[api_type]()
    except KeyError as e:
        print('The ' + api_type + ' DNS API is not be supported at persent')
        Logger.error('manual#get_api raise KeyError: ' + str(e))
        sys.exit()

def __get_aliyun_client():
    access_key_id = Config['api']['aliyun']['access_key_id']
    access_key_secret = Config['api']['aliyun']['access_key_secret']

    return api.Aliyun(access_key_id, access_key_secret)

def __extract_maindomain_and_challenge(domain):
    sudomain, maindomain = Utils.extract_domain(domain)

    acme_challenge = '_acme-challenge'

    if sudomain:
        acme_challenge += '.' + sudomain

    Logger.info('manual_hook maindomain: ' + maindomain)
    Logger.info('manual_hook acme_challenge: ' + acme_challenge)

    return (maindomain, acme_challenge)

def main():
    parser = argparse.ArgumentParser(description='example: python %s --auth --api aliyun' % os.path.basename(__file__))

    parser.add_argument('-a', '--auth', help='auth hook', action='store_true')
    parser.add_argument('-c', '--cleanup', help='cleanup hook', action='store_true')
    parser.add_argument('-t', '--test', help='test DNS API', action='store_true')
    parser.add_argument('--api', help='api type, default: aliyun', default='aliyun')
    parser.add_argument('--domain', help='a domain for test DNS API')

    args = parser.parse_args()

    Logger.info(args)

    if args.test:
        if args.domain is None:
            parser.error('-t, --test require --domain.')
        return test(args.domain, args.api)
    elif args.auth:
        auth(args.api)
    elif args.cleanup:
        cleanup(args.api)

if __name__ == '__main__':
    main()