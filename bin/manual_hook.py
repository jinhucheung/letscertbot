#!/usr/bin/env python
# coding: utf-8

import sys
import os
import time
import getopt
import logging

if sys.version_info < (3,0):
    import ConfigParser
else:
    import configparser as ConfigParser

current_path = os.path.split(os.path.realpath(__file__))[0]

# load api, lib
sys.path.append(os.path.sep.join([current_path, '..']))
import api

# load configuration
config_path = os.path.sep.join([current_path, '..', 'config.ini'])
config = ConfigParser.ConfigParser()
config.read(config_path)

# set logger
logger = logging.getLogger('logger')
if config.get('log', 'enable').lower() == 'true':
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=logging.DEBUG,
        filename=config.get('log', 'logfile'),
        filemode='a'
    )

def auth(type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')
        if 'CERTBOT_VALIDATION' not in os.environ:
            raise Exception('Environment variable CERTBOT_VALIDATION is empty.')

        certbot_domain = os.environ['CERTBOT_DOMAIN']
        certbot_validation = os.environ['CERTBOT_VALIDATION']
        certbot_acme_challenge = config.get('base', 'acme_challenge')

        logger.info('manual_hook#auth: Start to setting dns')
        logger.info('manual_hook#auth: ' + certbot_domain)
        logger.info('manual_hook#auth: ' + certbot_validation)

        client = __get_api_client(type)
        client.add_domain_record(certbot_domain, certbot_acme_challenge, certbot_validation)

        logger.info('manual_hook#auth: sleep 10 secs')
        time.sleep(10)

        logger.info('manual_hook#auth: Success.')
    except Exception as e:
        logger.error('manual_hook#auth raise Exception:' + str(e))
        sys.exit()

def cleanup(type = 'aliyun'):
    try:
        if 'CERTBOT_DOMAIN' not in os.environ:
            raise Exception('Environment variable CERTBOT_DOMAIN is empty.')

        certbot_domain = os.environ['CERTBOT_DOMAIN']
        certbot_acme_challenge = config.get('base', 'acme_challenge')

        logger.info('manual_hook#cleanup: Start to cleanup dns')
        logger.info('manual_hook#cleanup: ' + certbot_domain)

        client = __get_api_client(type)
        client.delete_domain_record(certbot_domain, certbot_acme_challenge)

        logger.info('manual_hook#cleanup: sleep 10 secs')
        time.sleep(10)

        logger.info('manual_hook#cleanup: Success.')
    except Exception as e:
        logger.error('manual_hook#cleanup raise Exception:' + e.message)
        sys.exit()

def usage():
    def printOpt(opt, desc):
        firstPartMaxLen = 30

        firstPart = '  ' + ', '.join(opt)
        secondPart = desc.replace('\n', '\n' + ' ' * firstPartMaxLen)

        delim = ''
        firstPartLen = len(firstPart)
        if firstPartLen >= firstPartMaxLen:
            spaceLen = firstPartMaxLen
            delim = '\n'
        else:
            spaceLen = firstPartMaxLen - firstPartLen

        delim = delim + ' ' * spaceLen
        print(firstPart + delim + secondPart)

    print('Usage: python %s [option] [arg] ...' % os.path.basename(__file__))
    print('Options:')
    printOpt(['-h', '--help'],
             'Display help information.')
    printOpt(['-a', '--auth'],
             'auth hook.')
    printOpt(['-c', '--cleanup'],
             'cleanup hook.')
    printOpt(['--api='],
             'api type, default: aliyun')
    print('Example: python %s --auth --api=aliyun' % os.path.basename(__file__))

def __get_api_client(type = 'aliyun'):
    try:
        switch = {
            'aliyun': __get_alidns_client
        }
        return switch[type]()
    except KeyError as e:
        logger.error('manual_hook#get_api raise KeyError: ' + str(e))
        raise SystemExit(e)

def __get_alidns_client():
    access_key_id = config.get('aliyun', 'access_key_id')
    access_key_secret = config.get('aliyun', 'access_key_secret')

    return api.AliDns(access_key_id, access_key_secret)

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            usage()
            raise Exception('')

        opts, args = getopt.getopt(
            sys.argv[1:],
            'hac',
            [
                'help',
                'auth',
                'cleanup',
                'api='
            ]
        )

        api_type = 'aliyun'
        hook_method = None

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
            elif opt in ('-a', '--auth'):
                hook_method = auth
            elif opt in ('-c', '--cleanup'):
                hook_method = cleanup
            elif opt in ('--api'):
                api_type = arg
            else:
                logger.error('Invalid option: ' + opt)

        if hook_method:
            hook_method(api_type)

    except getopt.GetoptError as e:
        logger.error('Error: ' + str(e) + '\n')
    except AttributeError as e:
        logger.error(e.args)
    except Exception as e:
        if str(e) != '':
            logger.error('Error: ' + str(e) + '\n')
        sys.exit()