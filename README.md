# Let's Certbot

Let's Certbot is a tool builds automated scripts base on [Certbot](https://certbot.eff.org/) for obtaining, renewing, deploying SSL certificates.

In order to verify your domains, Let's Certbot uses dns challenge on Certbot. Compared to http challenge, it means you can obtain a wildcard certificate and don't need to touch webserver.

On dns challenge, you need to set a TXT DNS record with specific contents on domain. Let's Certbot will help you do it via domain name registrar DNS API.

Supports domain name registrar at persent:

- [Aliyun](https://www.aliyun.com/)

## Installation

Let's Certbot as a Certbot tool requires Python 2.7 or 3.4+ running on a UNIX-like operation system.

First, you need to confirm if python is installed:

```
$ python --version
```

If everything is ok, get Certbot on [Official Document](https://certbot.eff.org/docs/install.html) for your system.

After installing Certbot, run Certbot with root:

```
$ sudo certbot --version
```

Clone this repository to get Let's Certbot:

```
$ git clone git@gitlab.bdachina.net:operation-group/letscertbot.git/letscertbot.git
```

Then copy configurations:

```
$ cd letscertbot
$ cp config.json.example config.json
```

## Usage

### Configuration

Before running Let's Certbot, you have the following configuration to change:

| Name                         | Required | Description                                               | Default               |
| ---------------------------- | -------- | --------------------------------------------------------- | --------------------- |
| base.email                   | true     | Email address for important renewal notifications         |                       |
| api.aliyun.access_key_id     | true     | AccessKey ID of Aliyun account                            |                       |
| api.aliyun.access_key_secret | true     | AccessKey Secret of Aliyun account                        |                       |
| log.enable                   | false    | Whether to enable log tracker                             | false                 |
| log.logfile                  | false    | The path of log file                                      | ./log/application.log |
| deploy.enable                | false    | Whether to run deployment script                          | false                 |
| deploy.keep_backups          | false    | The last n releases are kept for backups                  | 2                     |
| deploy.servers               | false    | The deployment servers                                    |                       |
| deploy.server.host           | false    | The host of deployment server, required on deploy         |                       |
| deploy.server.port           | false    | The port of deployment server SSH daemon                  | 22                    |
| deploy.server.user           | false    | The user of deployment server uses SSH login, run command | root                  |
| deploy.server.password       | false    | The password of deployment user                           |                       |
| deploy.server.deploy_to      | false    | The stored path of certificate                            | /etc/letsencrypt/live |
| deploy.server.nginx          | false    | The nginx settings of deploy server                       |                       |
| deploy.server.nginx.restart  | false    | Whether to restart nginx                                  | false                 |

In addition, `tlds.txt` contains some top level domains(TLD) and second level domains(SLD) for separating subdomain and main domain. If the TLD or SLD of your domain is not existed in `tlds.txt`, you need to append it in list.

### DNS API

Before obtaining certificate, you can run manual script (`manual.py`) to test DNS API with with your access key:

```
$ sudo python ./bin/manual.py --test --domain your.example.com --api aliyun
```

The script will place `_acme-challenge` TXT record under your domain via specified DNS API.

### Obtains

Run the obtainment script (`obtain.py`) with root for obtaining certificate:

```
$ sudo python ./bin/obtain.py -d your.example.com *.your.example.com
```

Then you will get a wildcard certificate names `your.example.com` in `/etc/letsencrypt/live/`

You can specify certificate name with `--cert` argument:

```
$ sudo python ./bin/obtain.py -d x.example.com y.example.com --cert xny.example.com
```

### Renewal

Renew certificates with the renewal script (`renewal.py`):

```
$ sudo python ./bin/renewal.py
```

Then Certbot will try renew all certificates which will be expired soon.

You can add renewal script as schedule task to `crontab`:

```
0 0 */7 * * sudo $your_letscertbot_home/bin/renewal.py > /var/log/letscertbot-renewal.log 2>&1
```

The task will run renewal script every 7 days.

If you need to force renew specified certificates, provide `--force` and `--certs` arguments:

```
$ sudo python ./bin/renewal.py --certs xny.example.com --force
```

### Deployment

If you set `deploy.enable` to true, Certbot will run the deployment script (`deploy.py`) on deploy hook. The script receives renewed certificate and push it to configured servers.

Let's Certbot deploys certificate via SSH, it means that local server runs Certbot must be able to connect deployment server. In order to connect, you need to **add the public key** of local server to deployment server or **provide `deploy.server.password` for `sshpass`**.

In order to add certificate to `deploy.server.deploy_to` or restart nginx, Let's Certbot requires `deploy.server.user` has permissions.

You can get deployment script by running the following command:

```
$ sudo python ./bin/deploy.py --check
```

And push certificate to server:

```
$ sudo python ./bin/deploy.py --push --cert $certificate_name --server $server_host
```

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