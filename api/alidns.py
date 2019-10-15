#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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

logger = logging.getLogger('logger')

class AliDns:
    __endpoint = 'https://alidns.aliyuncs.com'

    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    # @example alidns.add_domain_record("example.com", "_acme-challenge", "123456", "TXT")
    def add_domain_record(self, domain, rr, value, _type = 'TXT'):
        params = {
            'Action'     : 'AddDomainRecord',
            'DomainName' : domain,
            'RR'         : rr,
            'Type'       : _type,
            'Value'      : value
        }
        self.__request(params)

    # @example alidns.delete_domain_record("example.com", "_acme-challenge", "TXT")
    def delete_domain_record(self, domain, rr, _type = 'TXT'):
        params = {
            'Action'     : 'DeleteSubDomainRecords',
            'DomainName' : domain,
            'RR'         : rr,
            'Type'       : _type
        }
        self.__request(params)

    def to_string(self):
        return 'AliDns[access_key_id=' + self.access_key_id + ', access_key_secret=' + self.access_key_secret + ']'

    def __request(self, params):
        url = self.__compose_url(params)
        request = urllib2.Request(url)
        try:
            f = urllib2.urlopen(request)
            response = f.read().decode('utf-8')
            logger.info(response)
        except urllib2.HTTPError as e:
            logger.error('alidns#__request raise urllib2.HTTPError: ' + e.read().strip().decode('utf-8'))
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
        logger.info('Signature' + str(final_params['Signature']))

        url = '%s/?%s' % (self.__endpoint, urllib.urlencode(final_params))

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
            logger.error(e)

        if sys.version_info < (3,1):
            signature = base64.encodestring(digest).strip()
        else:
            signature = base64.encodebytes(digest).strip()

        return signature

    def __percent_encode(self, str):
        if sys.version_info <(3,0):
            res = urllib.quote(str.decode(sys.stdin.encoding).encode('utf8'), '')
        else:
            res = urllib.quote(str.encode('utf8'))
        res = res.replace('+', '%20')
        res = res.replace('\'', '%27')
        res = res.replace('\"', '%22')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')

        return res

if __name__ == '__main__':
    logger.info('开始调用阿里云 DNS API')
    logger.info('-'.join(sys.argv))

    _, action, certbot_domain, acme_challenge, certbot_validation, access_key_id, access_key_secret = sys.argv

    alidns = AliDns(access_key_id, access_key_secret)

    if 'add' == action:
        alidns.add_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'delete' == action:
        result = alidns.delete_domain_record(certbot_domain, acme_challenge)

    logger.info('结束调用阿里云 DNS API')