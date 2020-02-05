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
import json

if sys.version_info < (3,0):
    import urllib2
    import urllib
else:
    import urllib.request as urllib2
    import urllib.parse as urllib

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Logger

class Qcloud:
    __host = 'cns.api.qcloud.com'
    __path  = '/v2/index.php'

    def __init__(self, secret_id, secret_key):
        self.secret_id = secret_id
        self.secret_key = secret_key

    # @example qcloud.add_domain_record("example.com", "_acme-challenge", "123456", "TXT")
    def add_domain_record(self, domain, rr, value, _type = 'TXT'):
        params = {
            'Action'     : 'RecordCreate',
            'domain'     : domain,
            'subDomain'  : rr,
            'recordType' : _type,
            'recordLine' : '默认',
            'value'      : value
        }
        self.__request(params)

    # @example qcloud.delete_domain_record("example.com", "_acme-challenge", "TXT")
    def delete_domain_record(self, domain, rr, _type = 'TXT'):
        result = self.get_domain_records(domain, rr, _type)
        result = json.loads(result)

        for record in result['data']['records']:
            self.delete_domain_record_by_id(domain, record['id'])

    def delete_domain_record_by_id(self, domain, _id):
        params = {
            'Action'     : 'RecordDelete',
            'domain'     : domain,
            'recordId'   : _id
        }
        self.__request(params)

    def get_domain_records(self, domain, rr, _type = 'TXT'):
        params = {
            'Action'     : 'RecordList',
            'domain'     : domain,
            'subDomain'  : rr,
            'recordType' : _type
        }
        return self.__request(params)

    def to_string(self):
        return 'qcloud[secret_id=%s, secret_key=%s]' % (self.secret_id, self.secret_key)

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
            'SecretId'          : self.secret_id,
            'SignatureMethod'   : 'HmacSHA1',
            'Nonce'             : int(round(time.time() * 1000)),
            'Timestamp'         : int(time.time())
        }

        final_params = common_params.copy()
        final_params.update(params)

        final_params['Signature'] = self.__compute_signature(final_params)
        Logger.info('Signature ' + str(final_params['Signature']))

        url = 'https://%s%s?%s' % (self.__host, self.__path, urllib.urlencode(final_params))

        return url

    def __compute_signature(self, params):
        sorted_params = sorted(params.items(), key=lambda params: params[0])

        query_string = ''
        for (k, v) in sorted_params:
            query_string += '&' + self.__percent_encode(k) + '=' + str(v)

        string_to_sign = 'GET' + self.__host + self.__path + '?' + query_string[1:]

        try:
            if sys.version_info < (3,0):
                digest = hmac.new(str(self.secret_key), str(string_to_sign), hashlib.sha1).digest()
            else:
                digest = hmac.new(self.secret_key.encode(encoding="utf-8"), string_to_sign.encode(encoding="utf-8"), hashlib.sha1).digest()
        except Exception as e:
            Logger.error(e)

        if sys.version_info < (3,1):
            signature = base64.encodestring(digest).strip()
        else:
            signature = base64.encodebytes(digest).strip()

        return signature

    def __percent_encode(self, string):
        return string.replace('_', '.')

if __name__ == '__main__':
    Logger.info('开始调用腾讯云 DNS API')
    Logger.info('-'.join(sys.argv))

    _, action, certbot_domain, acme_challenge, certbot_validation, secret_id, secret_key = sys.argv

    qcloud = Qcloud(secret_id, secret_key)

    if 'add' == action:
        qcloud.add_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'delete' == action:
        qcloud.delete_domain_record(certbot_domain, acme_challenge)

    Logger.info('结束调用腾讯云 DNS API')