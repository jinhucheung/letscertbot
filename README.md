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