#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import urllib
import base64
import hashlib
import hmac
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

class Aliyun:
    __endpoint = 'alidns.aliyuncs.com'

    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    # @example aliyun.add_domain_record("example.com", "_acme-challenge", "123456", "TXT")
    def add_domain_record(self, domain, rr, value, _type = 'TXT'):
        params = {
            'Action'     : 'AddDomainRecord',
            'DomainName' : domain,
            'RR'         : rr,
            'Type'       : _type,
            'Value'      : value
        }
        self.__request(params)

    # @example aliyun.delete_domain_record("example.com", "_acme-challenge", "TXT")
    def delete_domain_record(self, domain, rr, _type = 'TXT'):
        params = {
            'Action'     : 'DeleteSubDomainRecords',
            'DomainName' : domain,
            'RR'         : rr,
            'Type'       : _type
        }
        self.__request(params)

    def to_string(self):
        return 'aliyun[access_key_id=%s, access_key_secret=%s]' % (self.access_key_id, self.access_key_secret)

    def __request(self, params):
        url = self.__compose_url(params)
        Logger.info('Request URL: ' + url)
        request = urllib2.Request(url)
        try:
            f = urllib2.urlopen(request, timeout=45)
            response = f.read().decode('utf-8')
            Logger.info(response)
            return response
        except urllib2.HTTPError as e:
            Logger.error('aliyun#__request raise urllib2.HTTPError: ' + str(e))
            raise SystemExit(e)

    def __compose_url(self, params):
        common_params = {
            'Format'        : 'JSON',
            'Version'       : '2015-01-09',
            'AccessKeyId'   : self.access_key_id,
            'SignatureVersion'  : '1.0',
            'SignatureMethod'   : 'HMAC-SHA1',
            'SignatureNonce'    : int(round(time.time() * 1000)),
            'Timestamp'         : time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        final_params = common_params.copy()
        final_params.update(params)

        final_params['Signature'] = self.__compute_signature(final_params)
        Logger.info('Signature ' + str(final_params['Signature']))

        url = 'https://%s/?%s' % (self.__endpoint, urllib.urlencode(final_params))

        return url

    def __compute_signature(self, params):
        sorted_params = sorted(params.items(), key=lambda params: params[0])

        query_string = ''
        for (k, v) in sorted_params:
            query_string += '&' +  self.__percent_encode(k) + '=' + self.__percent_encode(str(v))

        string_to_sign = 'GET&%2F&' + self.__percent_encode(query_string[1:])
        try:
            if sys.version_info < (3,0):
                digest = hmac.new(str(self.access_key_secret + "&"), str(string_to_sign), hashlib.sha1).digest()
            else:
                digest = hmac.new((self.access_key_secret + "&").encode(encoding="utf-8"), string_to_sign.encode(encoding="utf-8"), hashlib.sha1).digest()
        except Exception as e:
            Logger.error(e)

        if sys.version_info < (3,1):
            signature = base64.encodestring(digest).strip()
        else:
            signature = base64.encodebytes(digest).strip()

        return signature

    def __percent_encode(self, string):
        if sys.version_info <(3,0):
            res = urllib.quote(string.decode(sys.stdin.encoding).encode('utf8'), '')
        else:
            res = urllib.quote(string.encode('utf8'))
        res = res.replace('+', '%20')
        res = res.replace('\'', '%27')
        res = res.replace('\"', '%22')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')

        return res

if __name__ == '__main__':
    Logger.info('开始调用阿里云 DNS API')
    Logger.info('-'.join(sys.argv))

    _, action, certbot_domain, acme_challenge, certbot_validation, access_key_id, access_key_secret = sys.argv

    aliyun = Aliyun(access_key_id, access_key_secret)

    if 'add' == action:
        aliyun.add_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'delete' == action:
        aliyun.delete_domain_record(certbot_domain, acme_challenge)

    Logger.info('结束调用阿里云 DNS API')