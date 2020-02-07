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
import dns
from lib import Config, Logger, Utils

def auth(dns_type = 'aliyun'):
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

        client = __get_dns_client(dns_type)
        client.add_domain_record(maindomain, acme_challenge, certbot_validation)

        Logger.info('manual#auth: sleep %(time)i seconds' % { 'time' : __get_wait_time()})
        time.sleep(__get_wait_time())

        Logger.info('manual#auth: Success.')
    except Exception as e:
        Logger.error('manual#auth raise Exception:' + str(e))
        sys.exit()

def cleanup(dns_type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')

        certbot_domain = os.environ['CERTBOT_DOMAIN']

        Logger.info('manual#cleanup: Start to cleanup dns')
        Logger.info('manual#cleanup: ' + certbot_domain)

        maindomain, acme_challenge = __extract_maindomain_and_challenge(certbot_domain)

        client = __get_dns_client(dns_type)
        client.delete_domain_record(maindomain, acme_challenge)

        Logger.info('manual#cleanup: Success.')
    except Exception as e:
        Logger.error('manual#cleanup raise Exception:' + str(e))
        sys.exit()

def test(domain, dns_type = 'aliyun'):
    try:
        print('start to test ' + domain + ' in DNS ' + dns_type + ' API')

        client = __get_dns_client(dns_type)
        maindomain, acme_challenge = __extract_maindomain_and_challenge(domain)
        validation = ''.join(random.sample(string.ascii_letters + string.digits, 16))

        print('add TXT record(domain=' + maindomain + ', rr=' + acme_challenge + ', value=' + validation + ') to ' + dns_type + ' DNS')
        client.add_domain_record(maindomain, acme_challenge, validation)
        print('added TXT record')

        print('waiting %(time)i seconds...' % { 'time' : __get_wait_time()})
        time.sleep(__get_wait_time())

        print('remove above TXT record')
        client.delete_domain_record(maindomain, acme_challenge)
        print('removed TXT record')

        print('tested ' + domain + ' in DNS ' + dns_type + ' API')
    except Exception as e:
        Logger.error('test raise Exception:' + str(e))
        sys.exit()

def __get_dns_client(dns_type = 'aliyun'):
    try:
        data = Config['dns'][dns_type]

        if 'aliyun' == dns_type:
            return dns.Aliyun(data['access_key_id'], data['access_key_secret'])
        elif 'qcloud' == dns_type:
            return dns.Qcloud(data['secret_id'], data['secret_key'])
        elif 'godaddy' == dns_type:
            return dns.GoDaddy(data['api_key'], data['api_secret'])
        elif 'huaweicloud' == dns_type:
            return dns.HuaweiCloud(data['access_key_id'], data['secret_access_key'])
        raise KeyError(dns_type)
    except KeyError as e:
        print('The ' + dns_type + ' DNS API is not be supported at persent')
        Logger.error('manual#get_dns raise KeyError: ' + str(e))
        sys.exit()

def __extract_maindomain_and_challenge(domain):
    sudomain, maindomain = Utils.extract_domain(domain)

    acme_challenge = '_acme-challenge'

    if sudomain:
        acme_challenge += '.' + sudomain

    Logger.info('manual_hook maindomain: ' + maindomain)
    Logger.info('manual_hook acme_challenge: ' + acme_challenge)

    return (maindomain, acme_challenge)

def __get_wait_time():
    try:
        return int(Config['dns'].get('wait_time', 20))
    except:
        return 20

def main():
    parser = argparse.ArgumentParser(description='example: python %s --auth --dns aliyun' % os.path.basename(__file__))

    parser.add_argument('-a', '--auth', help='auth hook', action='store_true')
    parser.add_argument('-c', '--cleanup', help='cleanup hook', action='store_true')
    parser.add_argument('-t', '--test', help='test DNS API', action='store_true')
    parser.add_argument('--dns', help='dns type, default: aliyun', default='aliyun')
    parser.add_argument('-d', '--domain', help='a domain for test DNS API')

    args = parser.parse_args()

    Logger.info(args)

    if args.test:
        if args.domain is None:
            parser.error('-t, --test require --domain.')
        return test(args.domain, args.dns)
    elif args.auth:
        auth(args.dns)
    elif args.cleanup:
        cleanup(args.dns)

if __name__ == '__main__':
    main()