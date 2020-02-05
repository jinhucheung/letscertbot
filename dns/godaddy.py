#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import urllib
import json
import logging

if sys.version_info < (3,0):
    import urllib2
    import urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Logger

class GoDaddy:
    __host = 'api.godaddy.com'
    __path  = '/v1/domains'

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    # @example godaddy.add_domain_record("example.com", "_acme-challenge", "123456", "TXT")
    def add_domain_record(self, domain, rr, value, _type = 'TXT'):
        path = '/%s/records' % (domain)
        payload = [{
            'name'  : rr,
            'data'  : value,
            'type'  : _type,
            'ttl'   : 3600
        }]

        self.__request('PATCH', path, payload)

    # @example godaddy.delete_domain_record("example.com", "_acme-challenge", "TXT")
    # @link https://developer.godaddy.com/doc/endpoint/domains#/
    def delete_domain_record(self, domain, rr, _type = 'TXT'):
        '''
        Godaddy DNS API does not support deleting domain record
        '''

    # @example godaddy.get_domain_record("example.com", "_acme-challenge", "TXT")
    def get_domain_record(self, domain, rr, _type = 'TXT'):
        path = '/%(domain)s/records/%(type)s/%(rr)s' % {
            'domain'    : domain,
            'type'      : _type,
            'rr'        : rr
        }

        return self.__request('GET', path)

    def to_string(self):
        return 'godaddy[api_key=%s, , api_secret=%s]' % (self.api_key, self.api_secret)

    def __request(self, method, path, payload={}):
        url = 'https://%s%s%s' % (self.__host, self.__path, path)
        data = json.dumps(payload).encode('utf-8')
        Logger.info('Request URL: ' + url)
        Logger.info('Request Data: ' + str(data))

        request = urllib2.Request(url=url, data=data)
        request.add_header('Content-Type', 'application/json')
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'sso-key %s:%s' % (self.api_key, self.api_secret))
        request.get_method = lambda: method

        try:
            f = urllib2.urlopen(request, timeout=45)
            response = f.read().decode('utf-8')
            Logger.info(response)
            return response
        except urllib2.HTTPError as e:
            Logger.error('godaddy#__request raise urllib2.HTTPError: ' + str(e))
            raise SystemExit(e)

if __name__ == '__main__':
    Logger.info('开始调用 Godaddy DNS API')
    Logger.info('-'.join(sys.argv))

    _, action, certbot_domain, acme_challenge, certbot_validation, api_key, api_secret = sys.argv

    godaddy = GoDaddy(api_key, api_secret)

    if 'add' == action:
        godaddy.add_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'delete' == action:
        godaddy.delete_domain_record(certbot_domain, acme_challenge)
    elif 'get' == action:
        godaddy.get_domain_record(certbot_domain, acme_challenge)

    Logger.info('结束调用 Godaddy DNS API')