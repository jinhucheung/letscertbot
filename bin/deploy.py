#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])
certs_root_path = '/etc/letsencrypt/live'

sys.path.append(root_path)
from lib import Config, Logger, ScriptTemplates

def run():
    try:
        Logger.info('deploy#run deploy')

        if 'RENEWED_LINEAGE' not in os.environ:
            raise Exception('Environment variable RENEWED_LINEAGE is empty.')
        if 'RENEWED_DOMAINS' not in os.environ:
            raise Exception('Environment variable RENEWED_DOMAINS is empty.')

        Logger.info('deploy#run start to deploy cert: ' + os.environ['RENEWED_LINEAGE'])
        Logger.info('deploy#run deploy domains: ' + os.environ['RENEWED_DOMAINS'])

        deploy()

        Logger.info('deploy#run deployed cert')
    except Exception as e:
        Logger.error('deploy#run raise Exception:' + str(e))

def deploy():
    try:
        servers = Config['deploy'].get('servers', None)

        if not (servers and len(servers) > 0):
            print('deploy servers is empty in config file')
            return

        for server in servers:
            if not server:
                continue
            if server.get('enable', False):
                script = build_script(server)
                os.system(script)
                time.sleep(1)
            else:
                print('server host: ' + server.get('host', 'Undefined') + ' has been disable for deployment in config.json')
    except Exception as e:
        Logger.error('deploy#deploy raise Exception:' + str(e))

def check(cert_name, server_host):
    cert_path = os.path.sep.join([certs_root_path, cert_name or 'your_domain.com'])
    server = next((x for x in Config['deploy']['servers'] if x['host'] == server_host), {
        'host': server_host,
        'user': 'root'
    })
    script = build_script(server, cert_path)
    print(script)

def push(cert_name, server_host):
    try:
        cert_path = os.path.sep.join([certs_root_path, cert_name])
        server = next((x for x in Config['deploy']['servers'] if x['host'] == server_host), None)

        if server is None:
            raise Exception('Server host: ' + server_host + ' is not found in config.json')

        if not server.get('enable', False):
            print('server host: ' + server_host + ' has been disable for deployment in config.json')
            return

        script = build_script(server, cert_path)

        print('deploy#push start to run script:')
        os.system(script)
        print('deploy#push end script')
    except Exception as e:
        print("deploy#push raise Exception: " + str(e))

def build_script(server, cert_path = None):
    return ScriptTemplates.deploy_script({
        'cert_path': cert_path or os.environ['RENEWED_LINEAGE'],
        'deploy_to': server.get('deploy_to', None) or certs_root_path,
        'host': server['host'],
        'port': server.get('port', None) or 22,
        'user': server.get('user', None) or 'root',
        'password': server.get('password', ''),
        'restart_nginx': server.get('restart_nginx', False)
    })

def main():
    parser = argparse.ArgumentParser(description='example: python %s --check' % os.path.basename(__file__))

    parser.add_argument('-c', '--check', help='check deploy script', action='store_true')
    parser.add_argument('-p', '--push', help='push certificate to server', action='store_true')
    parser.add_argument('--cert', help='certificate name')
    parser.add_argument('--server', help='server host')

    args = parser.parse_args()

    if args.check:
        return check(args.cert, args.server)
    elif args.push:
        if args.cert is None or args.server is None:
            parser.error('-p, --push require --cert and --server.')
        return push(args.cert, args.server)

    run()

if __name__ == '__main__':
    main()
