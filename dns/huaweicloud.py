import json

class HuaweiCloud:
    __endpoint = 'https://dns.myhuaweicloud.com'

    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    # @example huaweicloud.add_domain_record("example.com", "_acme-challenge", "123456", "TXT")
    def add_domain_record(self, domain, rr, value, _type = 'TXT'):
        zone_id = self.get_domain_zone_id(domain)

        if not zone_id:
            return

        self.__request('POST', '/v2/zones/%s/recordsets' % (zone_id), {
            'name'      : '%s.%s.' % (rr, domain),
            'type'      : _type,
            'records'   : [ "\"%s\"" % (value) ]
        })

    # @example huaweicloud.delete_domain_record("example.com", "_acme-challenge", "TXT")
    def delete_domain_record(self, domain, rr, _type = 'TXT'):
        zone_id = self.get_domain_zone_id(domain)
        recordset_id = self.get_domain_recordset_id(domain, rr, _type)

        if not (zone_id and recordset_id):
            return

        self.__request('DELETE', '/v2/zones/%s/recordsets/%s' % (zone_id, recordset_id))

    # @example huaweicloud.get_domain_record("example.com", "_acme-challenge", "TXT")
    def get_domain_record(self, domain, rr, _type = 'TXT'):
        try:
            full_domain = '.'.join([rr, domain])
            response = self.__request('GET', 'v2/recordsets?type=%s&name=%s' % (_type, full_domain))
            content = json.loads(response.content)
            return filter(lambda record: record['name'][:-1] == full_domain and record['type'] == _type, content['recordsets'])[0]
        except Exception as e:
            Logger.error('huaweicloud#get_domain_record raise: ' + str(e))
            return None

    # @example huaweicloud.get_domain("example.com")
    def get_domain(self, domain):
        try:
            response = self.__request('GET', '/v2/zones?type=public&name=%s' % (domain))
            content = json.loads(response.content)
            return filter(lambda domain: domain['name'][:-1] == domain, content['zones'])[0]
        except Exception as e:
            Logger.error('huaweicloud#get_domain raise: ' + str(e))
            return None

    def get_domain_recordset_id(self, domain, rr, _type = 'TXT'):
        try:
            record = self.get_domain_record(domain, rr, _type)
            return record['id'] if record else None
        except Exception as e:
            Logger.error('huaweicloud#get_domain_recordset_id raise: ' + str(e))
            return None

    def get_domain_zone_id(self, domain):
        try:
            domain = self.get_domain(domain)
            return domain['id'] if domain else None
        except Exception as e:
            Logger.error('huaweicloud#get_domain_zone_id raise: ' + str(e))
            return None

    def to_string(self):
        return 'huaweicloud[access_key_id=%s, secret_access_key=%s]' % (self.access_key_id, self.secret_access_key)

    def __request(self, method, path, payload={}):
        return

if __name__ == '__main__':
    Logger.info('开始调用华为云 DNS API')
    Logger.info('-'.join(sys.argv))

    _, action, certbot_domain, acme_challenge, certbot_validation, api_key, api_secret = sys.argv

    huaweicloud = HuaweiCloud(api_key, api_secret)

    if 'add' == action:
        huaweicloud.add_domain_record(certbot_domain, acme_challenge, certbot_validation)
    elif 'delete' == action:
        huaweicloud.delete_domain_record(certbot_domain, acme_challenge)
    elif 'get' == action:
        huaweicloud.get_domain_record(certbot_domain, acme_challenge)

    Logger.info('结束调用华为云 DNS API')