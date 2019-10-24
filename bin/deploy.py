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
    ssh_options="-o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    timestamp=$(date +%%Y%%m%%d%%H%%M%%S)
    tmp_dir="/tmp/letscertbot-$timestamp"
    cert_name=$(basename '%(cert_path)s')

    server="%(user)s@%(host)s"
    deploy_path="%(deploy_to)s"
    deploy_cert_path="$deploy_path/$cert_name"
    backup_path="$deploy_path/backup"
    backup_cert_path="$backup_path/$cert_name"

    # define function
    alert () { echo "Alert: $1"; }
    success () { echo "\033[0;32mSuccess: $1\033[0m"; }
    cmd_info () { echo "\033[1;33mCommand: $1\033[0m"; }
    error () { echo "\033[0;31mError: $1\033[0m" >&2; exit 1; }

    run_remote () {
        cmd="$1"
        use_ssh=${2:-1}

        if [ $use_ssh -eq 1 ]; then
            [ -n "%(password)s" ] || ssh_options="$ssh_options -o BatchMode=yes"
            cmd="ssh $ssh_options -p %(port)s $server '$cmd'"
        fi
        [ -n "%(password)s" ] && cmd="sshpass -p %(password)s $cmd"

        cmd_info "$cmd"
        eval $cmd
    }

    # check sshpass if it is password mode
    if [ -n "%(password)s" ]; then
        alert "Checking if sshpass is installed:"
        [ "$(command -v sshpass)" ] || error "sshpass is not installed. In order to connect deployment server, you need to install sshpass"
        success "sshpass has been installed"
    fi

    alert "Trying connect to server by ssh:"
    run_remote "exit 0"
    [ $? -ne 0 ] && error "ssh connect to server $server failed"
    success "Connected to $server"

    alert "Creating tmp directory in server:"
    run_remote "mkdir -p $tmp_dir"
    [ $? -ne 0 ] && error "mkdir $tmp_dir in $server failed"
    success "Created tmp directory in $server"

    alert "Pushing cert files to server:"
    run_remote "scp $ssh_options -P %(port)s -r '%(cert_path)s' $server:$tmp_dir" 0
    [ $? -ne 0 ] && error "scp '%(cert_path)s' to $server:$tmp_dir failed"
    success "Pushed cert files to $server:$tmp_dir"

    alert "Cleaning up old backup cert in server:"
    run_remote "[ -d $backup_cert_path ]"
    if [ $? -eq 0 ]; then
        run_remote "rm -rf \"$backup_cert_path\""
        [ $? -ne 0 ] && error "Clean up old backup cert in $server failed"
        success "Cleaned up old backup cert in $server"
    else
        alert "It is not need to clean up beacause current backup files are not existed"
    fi

    alert "Backuping used cert in server:"
    run_remote "[ -d \"$deploy_cert_path\" ]"
    if [ $? -eq 0 ]; then
        run_remote "mkdir -p \"$backup_path\""
        [ $? -ne 0 ] && error "Create \"$backup_path\" in $server failed"
        run_remote "mv -Z \"$deploy_cert_path\" \"$backup_path\""
        [ $? -ne 0 ] && error "Move \"$deploy_cert_path\" to \"$backup_path\" in $server failed"
        success "Backuped cert into $backup_cert_path in $server"
    else
        alert "\"$deploy_cert_path\" is not found, not need to backup"
    fi

    alert "Trying create deploy to directory in server:"
    run_remote "mkdir -p $deploy_path"
    [ $? -ne 0 ] && error "Create $deploy_path directory in $server failed"
    success "Create $deploy_path directory in $server"

    alert "Moving new cert to deploy directory in server:"
    run_remote "mv -Z \"$tmp_dir/$cert_name\" \"$deploy_cert_path\""
    [ $? -ne 0 ] && error "Move \"$tmp_dir/$cert_name\" to \"$deploy_cert_path\" in $server failed"
    success "Moved new cert to $deploy_cert_path in $server"

    alert "Removing tmp directory in server:"
    run_remote "rm -r \"$tmp_dir\""
    [ $? -ne 0 ] && error "Remove \"$tmp_dir\" in $server failed"
    success "Moved new cert to $tmp_dir in $server"

    if [ "%(restart_nginx)i" -gt 0 ]; then
        alert "Trying restart nginx in server:"

        alert "Checking if nginx is installed:"
        run_remote "command -v nginx > /dev/null"
        [ $? -ne 0 ] && error "Nginx is not found, add nginx to PATH environment if nginx is installed"

        alert "Checking nginx configuration file:"
        run_remote "nginx -t 2> /dev/null"
        [ $? -ne 0 ] && error "Nginx configuration file test failed in $server"

        run_remote "command -v systemctl > /dev/null"
        if [ $? -eq 0 ]; then
            run_remote "systemctl reload nginx"
            [ $? -ne 0 ] && error "Restart nginx by 'systemctl reload nginx' in $server failed"
        else
            run_remote "command -v service > /dev/null"
            if [ $? -eq 0 ]; then
                run_remote "service reload nginx"
                [ $? -ne 0 ] && error "Restart nginx by 'service reload nginx' in $server failed"
            else
                run_remote "nginx -s reload"
                [ $? -ne 0 ] && error "nginx -s reload in $server failed"
            fi
        fi
        success "Restarted nginx in $server"
    fi
'''

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
        remotes = Config['deploy'].get('remotes', None)

        if not (remotes and len(remotes) > 0):
            print('deploy remotes is empty in config file')
            return

        for server in remotes:
            if not server:
                continue
            if server.get('enable', False):
                print('start to deploy server host: ' + server.get('host', 'Undefined'))
                script = build_script(server)
                os.system(script)
            else:
                print('server host: ' + server.get('host', 'Undefined') + 'has not enable deployment')
    except Exception as e:
        Logger.error('deploy#deploy raise Exception:' + str(e))

def check(cert_name, server_host):
    cert_path = os.path.sep.join([certs_root_path, cert_name or 'your_domain.com'])
    server = next((x for x in Config['deploy']['remotes'] if x['host'] == server_host), {
        'host': server_host,
        'user': 'root'
    })

    script = build_script(server, cert_path)

    print(script)

def push(cert_name, server_host):
    try:
        cert_path = os.path.sep.join([certs_root_path, cert_name])
        server = next((x for x in Config['deploy']['remotes'] if x['host'] == server_host), None)

        if server is None:
            raise Exception('Server host: ' + server_host + 'is not found in config.json')

        script = build_script(server, cert_path)

        print('deploy#push start to run script:')

        os.system(script)

        print('deploy#push end script')
    except Exception as e:
        print("deploy#push raise Exception: " + str(e))

def build_script(server, cert_path = None):
    user = server.get('usefalser', None) or 'root'
    password = server.get('password', '')
    port = server.get('port', None) or 22
    deploy_to = server.get('deploy_to', None) or certs_root_path
    restart_nginx = server.get('restart_nginx', False) or False

    return script_template % {
            'restart_nginx': restart_nginx,
            'cert_path': _escape(cert_path or os.environ['RENEWED_LINEAGE']),
            'host': _escape(server['host']),
            'port': _escape(port),
            'user': _escape(user),
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