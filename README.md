# Let's Certbot

[中文文档 Chinese document](/README-CN.md)

Let's Certbot is a tool builds automated scripts base on [Certbot](https://certbot.eff.org/) for obtaining, renewing, deploying SSL certificates.

In order to verify your domains, Let's Certbot uses dns challenge on Certbot. Compared to http challenge, it means you can obtain a wildcard certificate and don't need to touch webserver.

On dns challenge, you need to set a TXT DNS record with specific contents on domain. Let's Certbot will help you do it via domain name registrar DNS API.

Supports domain name registrar at persent:

- [Aliyun](https://www.aliyun.com/)
- [Tencent Cloud](https://cloud.tencent.com/)
- [Huawei Cloud](https://www.huaweicloud.com/)
- [GoDaddy](https://godaddy.com)

## Example

![example](https://user-images.githubusercontent.com/19590194/74025460-f62e0580-49de-11ea-989d-9dccf74439d6.gif)

## Installation

Let's Certbot as a Certbot tool supports docker and non-docker environments.

### Downloading Repository

Clone this repository to get Let's Certbot:

```
$ git clone git@github.com:jinhucheung/letscertbot.git
```

Then copy configurations:

```
$ cd letscertbot
$ cp config.json.example config.json
```

### Installing with Docker

Run Let's Certbot with Docker:

```
$ sudo docker run --rm --name letscertbot -v "$your_letscertbot_home/config.json:/app/config.json" -v "$your_letscertbot_home/tlds.txt:/app/tlds.txt" -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" jimcheung/letscertbot
```

You can run Let's Certbot with Compose if Docker Compose is installed:

```
$ sudo docker-compose run --rm app
```

### Installing without Docker

Let's Certbot requires Python 2.7 or 3.4+ running on a UNIX-like operation system.

First, you need to confirm if python is installed:

```
$ python --version
```

If everything is ok, get Certbot on [Official Document](https://certbot.eff.org/docs/install.html) for your system.

After installing Certbot, run Certbot with root:

```
$ sudo certbot --version
```

## Usage

### Configuration

Before running Let's Certbot, you have the following configuration to change:

| Name                        | Required | Description                                                                          | Default               |
| --------------------------- | -------- | ------------------------------------------------------------------------------------ | --------------------- |
| base.email                  | true     | Email address for important renewal notifications                                    |                       |
| dns                         | true     | dns settings                                                                         |                       |
| dns.wait_time               | false    | dns challenge wait time (seconds)                                                    | 20                    |
| dns.aliyun                  | false    | Access Key Id and Access Key Secret of Aliyun account                                |                       |
| dns.qcloud                  | false    | Secret Id and Secret Key of Tencent Cloud account                                    |                       |
| dns.godaddy                 | false    | API Key and API Secret of GoDaddy account                                            |                       |
| dns.huaweicloud             | false    | Access Key Id and Secret Access Key of Huawei Cloud account                          |                       |
| log.enable                  | false    | Whether to enable log tracker                                                        | false                 |
| log.logfile                 | false    | The path of log file                                                                 | ./log/application.log |
| deploy.servers              | false    | The deployment servers                                                               |                       |
| deploy.server.enable        | false    | Whether to run deployment script for server                                          | false                 |
| deploy.server.host          | false    | The host of deployment server, set "localhost" for local server, required on deploy. |                       |
| deploy.server.port          | false    | The port of remote server SSH daemon                                                 | 22                    |
| deploy.server.user          | false    | The user of remote server uses SSH login, run command                                | root                  |
| deploy.server.password      | false    | The password of remote user                                                          |                       |
| deploy.server.deploy_to     | false    | The stored path of certificate in server                                             | /etc/letsencrypt/live |
| deploy.server.restart_nginx | false    | Whether to restart nginx in server                                                   | false                 |
| deploy.server.after_hook    | false    | The command that server runs after successful deployment                             |                       |

In addition, `tlds.txt` contains some top level domains(TLD) and second level domains(SLD) for separating subdomain and main domain. If the TLD or SLD of your domain is not existed in `tlds.txt`, you need to append it in list.

### DNS API

Before obtaining certificate, you can run manual script (`manual.py`) to test DNS API with with your access key:

```
# Running with docker
$ sudo docker-compose run --rm app manual --test --domain your.example.com --dns aliyun

# Running without docker
$ sudo python ./bin/manual.py --test --domain your.example.com --dns aliyun
```

The script will place `_acme-challenge` TXT record under your domain via specified DNS API.

### Obtainment

Run the obtainment script (`obtain.py`) with root for obtaining certificate:

```
# Running with docker
$ sudo docker-compose run --rm app obtain -d your.example.com *.your.example.com

# Running without docker
$ sudo python ./bin/obtain.py -d your.example.com *.your.example.com
```

Then you will get a wildcard certificate names `your.example.com` in `/etc/letsencrypt/live/`

You can specify certificate name with `--cert` argument:

```
# Running with docker
$ sudo docker-compose run --rm app obtain -d x.example.com y.example.com --cert xny.example.com

# Running without docker
$ sudo python ./bin/obtain.py -d x.example.com y.example.com --cert xny.example.com
```

If your domain name registrar doesn't support api access, or if you're concerned about security problems from giving the access tokento your main domain, then you can use DNS alias argument:

```
$ sudo docker-compose run --rm app obtain -d x.main_domain.com y.main_domain.com --dns qcloud --challenge-alias alias_domain.com

# Running without docker
$ sudo python ./bin/obtain.py -d x.main_domain.com y.main_domain.com --dns qcloud --challenge-alias alias_domain.com
```

In the above command, Let's Certbot transfers `x.main_domain.com`, `y.main_domain.com` challenge to `alias_domain.com`, and sets the txt record of `alias_domain.com` via `qcloud` API. So you need to add CNAME record for challenged domain in advance:

```
_acme-challenge.x.main_domain.com => _acme-challenge.alias_domain.com
_acme-challenge.y.main_domain.com => _acme-challenge.alias_domain.com
```

### Renewal

Renew certificates with the renewal script (`renewal.py`):

```
# Running with docker
$ sudo docker-compose run --rm app renewal

# Running without docker
$ sudo python ./bin/renewal.py
```

Then Certbot will try renew all certificates which will be expired soon.

You can add renewal script as schedule task to `crontab`:

```
# Running with docker
0 0 */7 * * sudo docker-compose -f $your_letscertbot_home/docker-compose.yml run --rm app renewal > /var/log/letscertbot-renewal.log 2>&1

# Running without docker
0 0 */7 * * sudo $your_letscertbot_home/bin/renewal.py > /var/log/letscertbot-renewal.log 2>&1
```

The task will run renewal script every 7 days.

If you need to force renew specified certificates, provide `--force` and `--certs` arguments:

```
# Running with docker
$ sudo docker-compose run --rm app renewal --certs xny.example.com --force

# Running without docker
$ sudo python ./bin/renewal.py --certs xny.example.com --force
```

### Deployment

If you set `deploy.server.enable` to true, Certbot will run the deployment script (`deploy.py`) on deploy hook. The script receives renewed certificate and push it to configured servers.

Let's Certbot deploys certificate to remote server via SSH, it means that local server runs Certbot must be able to connect remote server. In order to connect, you need to **add the public key** of local server to remote server or **provide `deploy.server.password`** for `sshpass`.

In order to add certificate to `deploy.server.deploy_to` or restart nginx, Let's Certbot requires `deploy.server.user` has permissions.

You can get deployment script by running the following command:

```
# Running with docker
$ sudo docker-compose run --rm app deploy --check

# Running without docker
$ sudo python ./bin/deploy.py --check
```

And push certificate to server:

```
# Running with docker
$ sudo docker-compose run --rm app deploy --push --cert $certificate_name --server $server_host

# Running without docker
$ sudo python ./bin/deploy.py --push --cert $certificate_name --server $server_host
```

**Note**: If `deploy.server` enables SELinux in enforcing mode, you need to confirm that nginx has access to the SElinux security context of `deploy.server.deploy_to`.

**Note**: If you run Let's Certbot via container and restart nginx in local server, you should set local server as remote.

## Thanks

- [Certbot](https://github.com/certbot/certbot)
- [letsencrypt-aliyun-dns-manual-hook](https://github.com/broly8/letsencrypt-aliyun-dns-manual-hook)
- [certbot-letencrypt-wildcardcertificates-alydns-au](https://github.com/ywdblog/certbot-letencrypt-wildcardcertificates-alydns-au)

## Contributing

Bug report or pull request are welcome.

1. Fork it
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)

Please write unit test with your code if necessary.

## License

The repository is available as open source under the terms of the [MIT License](MIT-LICENSE).