#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import urllib
import json

if sys.version_info < (3,0):
    import urllib2
    import urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Logger, Utils

class Cloudflare:
    __host = 'api.cloudflare.com'
    __path  = '/client/v4/zones'

    def __init__(self, email, api_key, api_token):
        self.email = email
        self.api_key = api_key
        self.api_token = api_token

    # @example cloudflare.add_domain_record("example.com", "_acme-challenge", "123456", "TXT")
    # @link https://api.cloudflare.com/#dns-records-for-a-zone-create-dns-record
    def add_domain_record(self, domain, rr, value, _type = 'TXT'):
        zone_id = self.get_domain_zone_id(domain)
        if zone_id:
            try:
                path = '/%s/dns_records' % (zone_id)
                payload = {
                    'name'    : '%s.%s' % (rr, domain),
                    'type'    : _type,
                    'content' : value,
                    'ttl'     : 120,
                    'proxied' : False
                }
                return self.__request('POST', path, payload)
            except Exception as e:
                Logger.error(e)
        return

    # @example cloudflare.delete_domain_record("example.com", "_acme-challenge", "123456")
    # @link https://api.cloudflare.com/#dns-records-for-a-zone-delete-dns-record
    def delete_domain_record(self, domain, rr, value, _type = 'TXT'):
        records = self.get_domain_records(domain, rr, _type)
        if records:
            for record in records:
                try:
                    self.__request('DELETE', '/%s/dns_records/%s' % (record['zone_id'], record['id']))
                except Exception as e:
                    Logger.error(e)
        return

    # @example cloudflare.get_domain_record("example.com", "_acme-challenge", "TXT")
    def get_domain_record(self, domain, rr, _type = 'TXT'):
        records = self.get_domain_records(domain, rr, _type, 1)
        return records[0] if records else None

    def get_domain_records(self, domain, rr, _type = 'TXT', per_page = 100):
        zone_id = self.get_domain_zone_id(domain)
        if zone_id:
            try:
                path = '/%s/dns_records?match=all&type=%s&name=%s.%s&per_page=%s' % (zone_id, _type, rr, domain, per_page)
                response = self.__request('GET', path)
                content = json.loads(response)
                if content['success'] and content['result']:
                    return content['result']
            except Exception as e:
                Logger.error(e)
        return


    def get_domain_zone_id(self, domain):
        guesses_zone_names = Utils.guess_domain_names(domain)

        for zone_name in guesses_zone_names:
            try:
                path = '?per_page=1&match=all&name=%s' % (zone_name)
                response = self.__request('GET', path)
                content = json.loads(response)
                if content['success'] and content['result'] and content['result'][0]:
                    return content['result'][0]['id']
            except Exception as e:
                Logger.error(e)
        return

    def to_string(self):
        return 'cloudflare[email=%s, api_key=%s, , api_token=%s]' % (self.email, self.api_key, self.api_token)

    def __request(self, method, path, payload={}):
        url = 'https://%s%s%s' % (self.__host, self.__path, path)
        data = json.dumps(payload).encode('utf-8')
        Logger.info('Request URL: ' + url)
        Logger.info('Request Data: ' + str(data))

        request = urllib2.Request(url=url, data=data)
        request.add_header('Content-Type', 'application/json')
        request.add_header('Accept', 'application/json')

        if self.api_token:
            request.add_header('Authorization', 'Bearer %s' % (self.api_token))
        elif self.email and self.api_key:
            request.add_header('X-Auth-Email', self.email)
            request.add_header('X-Auth-Key', self.api_key)

        request.get_method = lambda: method

        try:
            f = urllib2.urlopen(request, timeout=45)
            response = f.read().decode('utf-8')
            Logger.info(response)
            return response
        except urllib2.HTTPError as e:
            Logger.error('cloudflare#__request raise urllib2.HTTPError: ' + str(e))
            if e.code != 403:
                raise SystemExit(e)

if __name__ == '__main__':
    Logger.info('开始调用 Cloudflare DNS API')
    Logger.info(' '.join(sys.argv))

    _, action, certbot_domain, acme_challenge, certbot_validation, email, api_key, api_token = sys.argv
    api_token = None if api_token == '_' else api_token

    cloudflare = Cloudflare(email, api_key, api_token)

    if 'add' == action:
        cloudflare.add_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'delete' == action:
        cloudflare.delete_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'get' == action:
        cloudflare.get_domain_record(certbot_domain, acme_challenge)

    Logger.info('结束调用 Cloudflare DNS API')
