#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])
tlds_path = os.path.sep.join([root_path, 'tlds.txt'])

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


if __name__ == '__main__':
    domains = sys.argv[1:]

    print('(sudomain, maindomain)')

    for domain in domains:
        print(extract_domain(domain))