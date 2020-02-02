#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import textwrap

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])
sys.path.append(root_path)

from lib import Utils

def deploy_script(options):
    return DeployScriptTemplate(options).build()

class BaseScriptTemplate(object):
    def __init__(self, options):
        self.options = options

    def escape(self, string):
        return str(string).replace("'", "\\'").replace('"', '\\"').replace(' ', '\\ ')

    def escape_options(self, key):
        return self.escape(self.options[key])

class DeployScriptTemplate(BaseScriptTemplate):
    def __init__(self, options):
        super(DeployScriptTemplate, self).__init__(options)

        self.is_localhost = Utils.is_localhost(options['host'])

    def build(self):
        return os.linesep.join([
            self.build_common_script(),
            (self.build_locale_script() if self.is_localhost else self.build_remote_script()),
            self.build_migrate_script(),
            self.build_nginx_script()
        ])

    def build_common_script(self):
        script = textwrap.dedent('''
            # define variables
            timestamp=$(date +%%Y%%m%%d%%H%%M%%S)
            tmp_dir="/tmp/letscertbot-$timestamp"

            cert_path='%(cert_path)s'
            cert_name=$(basename $cert_path)

            deploy_path="%(deploy_to)s"
            deploy_cert_path="$deploy_path/$cert_name"
            backup_path="$deploy_path/backup"
            backup_cert_path="$backup_path/$cert_name"

            # define function
            alert () { echo "Alert: $1"; }
            success () { echo -e "\033[32mSuccess: $1\033[0m"; }
            cmd_info () { echo -e "\033[33mCommand: $1\033[0m"; }
            warning () { echo -e "\033[31mWarning: $1\033[0m"; }
            error () { echo -e "\033[31mError: $1\033[0m" >&2; exit 1; }
        ''')

        return script % {
            'cert_path': self.escape_options('cert_path'),
            'deploy_to': self.escape_options('deploy_to')
        }

    def build_locale_script(self):
        return textwrap.dedent('''
            server="%(host)s"

            alert "Start to deploy $server"

            run () {
                cmd_info "$1"
                eval "$1"
            }

            copy_certs () {
                run "cp -rL $cert_path $tmp_dir"
            }
        ''') % {
            'host': self.escape_options('host')
        }

    def build_remote_script(self):
        return textwrap.dedent('''
            ssh_options="-o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=60"
            server="%(user)s@%(host)s"
            port="%(port)s"
            password="%(password)s"

            alert "Start to deploy $server"

            run () {
                cmd="$1"
                use_ssh=${2:-1}

                if [ $use_ssh -eq 1 ]; then
                    [ "$password" ] || ssh_batch_mode="-o BatchMode=yes"
                    cmd="ssh $ssh_options $ssh_batch_mode -p $port $server '$cmd'"
                fi
                [ "$password" ] && cmd="sshpass -p $password $cmd"

                cmd_info "$cmd"
                eval $cmd
            }

            copy_certs () {
                run "scp $ssh_options -P $port -r $cert_path $server:$tmp_dir" 0
            }

            # check sshpass if it is password mode
            if [ "$password" ]; then
                alert "Checking if sshpass is installed in localhost:"
                [ "$(command -v sshpass)" ] || error "sshpass is not installed. In order to connect $server, you need to install sshpass"
                success "sshpass has been installed"
            fi

            alert "Trying connect to $server by ssh:"
            run "exit 0"
            [ $? -ne 0 ] && error "ssh connect to server $server failed"
            success "Connected to $server"
        ''') % {
            'user': self.escape_options('user'),
            'host': self.escape_options('host'),
            'port': self.escape_options('port'),
            'password': self.escape_options('password')
        }

    def build_migrate_script(self):
        return textwrap.dedent('''
            overmv='mv'
            alert "Check mv if it is support '-Z' options in $server:"
            run "command -v man > /dev/null"
            if [ $? -eq 0 ]; then
                run "man mv | grep \\"\-Z\\""
            else
                run "mv --help | grep \\"\-Z\\""
            fi
            [ $? -eq 0 ] && overmv="$overmv -Z"

            alert "Creating tmp directory in $server:"
            run "mkdir -p $tmp_dir"
            [ $? -ne 0 ] && error "mkdir $tmp_dir in $server failed"
            success "Created tmp directory in $server"

            alert "Pushing cert files to $server:"
            copy_certs
            [ $? -ne 0 ] && error "Copy $cert_path to $server:$tmp_dir failed"
            success "Pushed cert files to $server:$tmp_dir"

            alert "Cleaning up old backup cert in $server:"
            run "[ -d $backup_cert_path ]"
            if [ $? -eq 0 ]; then
                run "rm -rf \"$backup_cert_path\""
                [ $? -ne 0 ] && error "Clean up old backup cert in $server failed"
                success "Cleaned up old backup cert in $server"
            else
                alert "It is not need to clean up beacause current backup files are not existed"
            fi

            alert "Backuping used cert in $server:"
            run "[ -d \"$deploy_cert_path\" ]"
            if [ $? -eq 0 ]; then
                run "mkdir -p \"$backup_path\""
                [ $? -ne 0 ] && error "Create \"$backup_path\" in $server failed"
                run "cp -rL \"$deploy_cert_path\" \"$backup_path\""
                [ $? -ne 0 ] && error "Copy \"$deploy_cert_path\" to \"$backup_path\" in $server failed"
                success "Backuped cert into $backup_cert_path in $server"
            else
                alert "\"$deploy_cert_path\" is not found, not need to backup"
            fi

            alert "Trying create deploy directory in $server:"
            run "mkdir -p \"$deploy_cert_path\""
            [ $? -ne 0 ] && error "Create $deploy_cert_path directory in $server failed"
            success "Create $deploy_cert_path directory in $server"

            alert "Trying move cert files to the symblinks of deploy files in $server:"
            symblink_pipeline='basename %% | xargs -i sh -c \\"readlink $deploy_cert_path/{} || echo {}\\" | xargs -i sh -c \\"[ \\"{}:0:1\\" = / ] && echo {} || echo $deploy_cert_path/{}\\" | xargs -i $overmv -f %% {}'
            symblink_pipeline=$(echo $symblink_pipeline | sed "s~\$deploy_cert_path~$deploy_cert_path~g" | sed "s~\$overmv~$overmv~g")
            run "ls -d $tmp_dir/$cert_name/* | xargs -I %% sh -c \\"$symblink_pipeline\\""
            if [ $? -ne 0 ]; then
                warning "Move cert files to the symblinks of deploy files in $server failed"

                alert "Trying move current deploy directory to tmp directory in $server:"
                run "$overmv \"$deploy_cert_path\" \"$deploy_cert_path-$timestamp\""
                [ $? -ne 0 ] && error "Move current deploy directory to tmp directory in $server failed"

                alert "Trying overwrite deploy directory in $server:"
                run "$overmv \"$tmp_dir/$cert_name\" \"$deploy_cert_path\""
                if [ $? -ne 0 ]; then
                    run "$overmv \"$deploy_cert_path-$timestamp\" \"$deploy_cert_path\""
                    error "Move \"$tmp_dir/$cert_name\" to \"$deploy_cert_path\" in $server failed"
                fi

                alert "Trying remove tmp deploy directory in $server:"
                run "rm -rf \"$deploy_cert_path-$timestamp\""
                [ $? -ne 0 ] && error "Remove \"$deploy_cert_path-$timestamp\" in $server failed"
            fi
            success "Moved new cert to $deploy_cert_path in $server"

            alert "Removing tmp directory in $server:"
            run "rm -rf \"$tmp_dir\""
            [ $? -ne 0 ] && error "Remove \"$tmp_dir\" in $server failed"
            success "Moved new cert to $tmp_dir in $server"
        ''')

    def build_nginx_script(self):
        if not self.options.get('restart_nginx', False):
            return ''

        return textwrap.dedent('''
            alert "Trying restart nginx in $server:"

            alert "Checking if nginx is installed:"
            run "command -v nginx > /dev/null"
            [ $? -ne 0 ] && error "Nginx is not found, add nginx to PATH environment if nginx is installed"

            alert "Checking nginx configuration file:"
            run "nginx -t 2> /dev/null"
            [ $? -ne 0 ] && error "Nginx configuration file test failed in $server"

            run "command -v systemctl > /dev/null"
            if [ $? -eq 0 ]; then
                run "systemctl reload nginx"
                [ $? -ne 0 ] && error "Restart nginx by 'systemctl reload nginx' in $server failed"
            else
                run "command -v service > /dev/null"
                if [ $? -eq 0 ]; then
                    run "service nginx restart"
                    [ $? -ne 0 ] && error "Restart nginx by 'service nginx restart' in $server failed"
                else
                    run "nginx -s reload"
                    [ $? -ne 0 ] && error "nginx -s reload in $server failed"
                fi
            fi
            success "Restarted nginx in $server"
        ''')

if __name__ == '__main__':
    print(deploy_script({
        'host': 'localhost',
        'cert_path': '/etc/letsencrpyt/live/your.domain.com',
        'deploy_to': '/root/letsencrpyt/live',
        'restart_nginx': True,
    }))

    print(deploy_script({
        'host': '192.168.1.1',
        'port': 22,
        'user': 'root',
        'password': 'root',
        'cert_path': '/etc/letsencrpyt/live/your.domain.com',
        'deploy_to': '/root/letsencrpyt/live',
        'restart_nginx': True,
    }))