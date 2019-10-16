#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

sys.path.append(root_path)
from lib import Config, Logger

deploy_script_template = '''
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
    run_remote "exit $(ls $backup_path 2>/dev/null | wc -l)"
    if [ "$?" -ge "$keep_backups" ]; then
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
    success "Moved new cert to $tmp_dir in $server"

    if [ "%(restart_nginx)i" -gt 0 ]; then
        info "Trying restart nginx in server:"

        info "Checking if nginx is installed:"
        run_remote "command -v nginx"
        [ $? -ne 0 ] && error "nginx is not found, add nginx to PATH environment if nginx is installed"

        info "Checking nginx configuration file:"
        run_remote "nginx -t 2> /dev/null"
        [ $? -ne 0 ] && error "nginx configuration file test failed in $server"

        run_remote "command -v systemctl"
        if [ $? -eq 0 ]; then
            run_remote "systemctl reload nginx"
        else
            run_remote "command -v service"
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
        if not Config['deploy']['enable']:
            raise Exception('deploy setting is disabled in config file')

        if 'RENEWED_LINEAGE' not in os.environ:
            raise Exception('Environment variable RENEWED_LINEAGE is empty.')
        if 'RENEWED_DOMAINS' not in os.environ:
            raise Exception('Environment variable RENEWED_DOMAINS is empty.')

        Logger.info('deploy_hook#run start to deploy cert: ' + os.environ['RENEWED_LINEAGE'])
        Logger.info('deploy_hook#run deploy domains: ' + os.environ['RENEWED_DOMAINS'])

        deploy()

        Logger.info('deploy_hook#run deployed cert')
    except Exception as e:
        Logger.error('deploy_hook#run raise Exception:' + str(e))

def deploy():
    try:
        servers = Config['deploy']['servers']

        if not (servers and len(servers) > 0):
            raise Exception('deploy servers is empty in config file')

        for server in servers:
            deploy_script = build_script(server)

            os.system(deploy_script)
    except Exception as e:
        Logger.error('deploy_hook#deploy raise Exception:' + str(e))

def build_script(server):
    restart_nginx = Config['deploy']['restart_nginx'] if 'restart_nginx' in Config['deploy'] else False
    keep_backups = Config['deploy']['keep_backups'] if ('keep_backups' in Config['deploy']) and Config['deploy']['keep_backups'] else 2
    password = server['password'] if 'password' in server else ''
    port = server['port'] if ('port' in server) and server['port'] else 22
    deploy_to = server['deploy_to'] if ('deploy_to' in server) and server['deploy_to'] else '/etc/letsencrypt/live'

    return deploy_script_template % {
            'restart_nginx': restart_nginx,
            'keep_backups': keep_backups,
            'cert_path': _escape(os.environ['RENEWED_LINEAGE']),
            'host': _escape(server['host']),
            'port': _escape(port),
            'user': _escape(server['user']),
            'password': _escape(password),
            "deploy_to": _escape(deploy_to),
        }

def _escape(string):
    return str(string).replace("'", "\\'").replace('"', '\\"').replace(' ', '\\ ')

if __name__ == '__main__':
    Logger.info('deploy hook')
    run()
    Logger.info('deployed hook')
