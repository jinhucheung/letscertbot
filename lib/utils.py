#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])
tlds_path = os.path.sep.join([root_path, 'tlds.txt'])

sys.path.append(root_path)
from lib import Config

# @example extract_domain('m.domain.com') #=> ('m', 'domain.com')
def extract_domain(domain):
    parts = domain.split('.')

    if len(parts) > 2:
        with open(tlds_path) as f:
            tlds = f.readlines()
            tlds = map(lambda tld: tld.strip().lower(), tlds)

        tld_index = -3 if '.'.join(parts[-2:]).lower() in tlds else -2

        return ('.'.join(parts[:tld_index]), '.'.join(parts[tld_index:]))

    return ('', domain)

def guess_domain_names(domain):
    fragments = domain.split('.')
    return ['.'.join(fragments[i:]) for i in range(0, len(fragments))]

def is_enable_deployment():
    try:
        deploy = Config.get('deploy', {})
        servers = deploy.get('servers', [])

        for server in servers:
            if server and server.get('enable', False):
                return True
        return False
    except Exception as e:
        print("utils#is_enable_deployment raise Exception: " + str(e))
        return False

def is_localhost(host):
    return host in ['127.0.0.1', '0.0.0.0', '::1', 'localhost']

if __name__ == '__main__':
    domains = sys.argv[1:]

    print('Testing extract_domain...')
    print('(sudomain, maindomain)')
    for domain in domains:
        print(extract_domain(domain))

    print('Testing is_enable_deployment...')
    print(is_enable_deployment())

    print('Testing is_localhost...')
    print(is_localhost('127.0.0.1'))
    print(is_localhost('127.0.0.2'))