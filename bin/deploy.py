#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])
certs_root_path = '/etc/letsencrypt/live'

sys.path.append(root_path)
from lib import Config, Logger

script_template = '''
    # define variables
    timestamp=$(date +%%+4Y%%m%%d%%H%%M%%S)
    tmp_dir="/tmp/letscertbot-$timestamp"
    cert_name=$(basename '%(cert_path)s')

    server="%(user)s@%(host)s"
    deploy_path="%(deploy_to)s/$cert_name"
    backup_path="%(deploy_to)s/backup/$cert_name"
    keep_backups=%(keep_backups)s

    # define function
    info () { echo "Info: $1"; }
    success () { echo "\033[0;32mSuccess: $1\033[0m"; }
    error () { echo "\033[0;31mError: $1\033[0m" >&2; exit 1; }

    run_remote () {
        cmd="$1"
        use_ssh=${2:-1}

        [ $use_ssh -eq 1 ] && cmd="ssh -p %(port)s $server '$cmd'"
        [ -n "%(password)s" ] && cmd="sshpass -p %(password)s $cmd"

        info "$cmd"
        eval $cmd
    }

    # check sshpass if it is password mode
    if [ -n "%(password)s" ]; then
        info "Checking if sshpass is installed:"
        [ "$(command -v sshpass)" ] || error "sshpass is not installed"
        success "sshpass has been installed"
    fi

    info "Trying connect to server by ssh:"
    run_remote "exit 0"
    [ $? -ne 0 ] && error "ssh connect failed to server $server"
    success "Connected to $server"

    info "Creating tmp directory in server:"
    run_remote "mkdir -p $tmp_dir"
    success "Created tmp directory in $server"

    info "Copying cert files to server:"
    run_remote "scp -o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P %(port)s -r '%(cert_path)s' $server:$tmp_dir" 0
    success "Copyed cert files to $server:$tmp_dir"

    info "Cleaning up old backup cert in server:"
    run_remote "ls $backup_path 2>/dev/null | wc -l | xargs -I {} [ {} -ge $keep_backups ] && exit 1 || exit 0"
    if [ "$?" -ge 1 ]; then
        run_remote "ls $backup_path -t | tail -1 | xargs -I {} rm -r \"$backup_path/{}\""
        success "Cleaned up old backup cert in $server"
    else
        info "It is not need to clean up beacause current backup size less than $keep_backups"
    fi

    info "Backuping used cert in server:"
    run_remote "mkdir -p $backup_path"
    run_remote "[ -d \"$deploy_path\" ] && mv \"$deploy_path\" \"$backup_path/$timestamp\""
    success "Backuped cert into $backup_path in $server"

    info "Moving new cert to deploy directory in server:"
    run_remote "mv \"$tmp_dir/$cert_name\" \"$deploy_path\""
    success "Moved new cert to $deploy_path in $server"

    info "Removing tmp directory in server:"
    run_remote "rm -r \"$tmp_dir\""
    success "Moved new cert to $tmp_dir incert_root_pathver"

    if [ "%(restart_nginx)i" -gt 0 ]; thencert_root_path
        info "Trying restart nginx in server:"

        info "Checking if nginx is installed:"
        run_remote "command -v nginx > /dev/null"
        [ $? -ne 0 ] && error "nginx is not found, add nginx to PATH environment if nginx is installed"

        info "Checking nginx configuration file:"
        run_remote "nginx -t 2> /dev/null"
        [ $? -ne 0 ] && error "nginx configuration file test failed in $server"

        run_remote "command -v systemctl > /dev/null"
        if [ $? -eq 0 ]; then
            run_remote "systemctl reload nginx"
        else
            run_remote "command -v service > /dev/null"
            if [ $? -eq 0 ]; then
                run_remote "service reload nginx"
            else
                run_remote "nginx -s reload"
            fi
        fi
        success "Restarted nginx in $server"
    fi
'''

def run():
    try:
        Logger.info('deploy#run deploy')

        if not Config['deploy']['enable']:
            raise Exception('deploy setting is disabled in config file')

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
        servers = Config['deploy']['servers']

        if not (servers and len(servers) > 0):
            raise Exception('deploy servers is empty in config file')

        for server in servers:
            script = build_script(server)

            os.system(script)
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
            raise Exception('Server host: ' + server_host + 'is not found in config.json')

        script = build_script(server, cert_path)

        print('deploy#push start to run script:')
        print(script)

        os.system(script)

        print('deploy#push end script')
    except Exception as e:
        print("deploy#push raise Exception: " + str(e))

def build_script(server, cert_path = None):
    keep_backups = Config['deploy']['keep_backups'] if 'keep_backups' in Config['deploy'] and Config['deploy']['keep_backups'] else 2
    password = server['password'] if 'password' in server else ''
    port = server['port'] if 'port' in server and server['port'] else 22
    deploy_to = server['deploy_to'] if 'deploy_to' in server and server['deploy_to'] else certs_root_path
    restart_nginx = server['nginx']['restart'] if 'nginx' in server and 'restart' in server['nginx'] else False

    return script_template % {
            'restart_nginx': restart_nginx,
            'keep_backups': keep_backups,
            'cert_path': _escape(cert_path or os.environ['RENEWED_LINEAGE']),
            'host': _escape(server['host']),
            'port': _escape(port),
            'user': _escape(server['user']),
            'password': _escape(password),
            "deploy_to": _escape(deploy_to),
        }

def _escape(string):
    return str(string).replace("'", "\\'").replace('"', '\\"').replace(' ', '\\ ')

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