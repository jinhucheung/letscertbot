# Let's Certbot

[Certbot](https://certbot.eff.org/) 是 [Let's Encrypt](https://letsencrypt.org/) 官方推荐的自动签发 SSL 免费证书工具。

## 安装 Certbot

Certbot 依赖于 Python 2.7 或 3.4+ 的环境。在安装 Certbot 前，须确保 Python 已经安装。

下面参考官方文档<sup>[[1]](#get_certbot)</sup>，在 Ubuntu 环境进行安装。

添加 Certbot 官方源:

```sh
$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository universe
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
```

然后执行安装 Certbot:

```sh
$ sudo apt-get install certbot
```

## 申请证书

Certbot 默认会写入 `/etc/letsencrypt`, `/var/log/letencrypt`, `/var/lib/letsencrypt` 文件，所以须使用 root 进行申请。

现在执行下面命令为 `xxx.com` 域名(更改为你所需的域名)申请通配符证书:

```sh
$ sudo certbot --server https://acme-v02.api.letsencrypt.org/directory -d "*.xxx.com" -d "xxx.com" --manual --preferred-challenges dns-01 certonly
```

**Note**: 如果申请通配符证书，只申请通配符域名(如 `*.xxx.com`), 其将匹配不到主域名(如 `xxx.com`), 所以需要添加主域名到证书覆盖范围。

## 续期证书

--server https://acme-v02.api.letsencrypt.org/directory -d "*.xpicker.me" -d "xpicker.me" --manual --preferred-challenges dns-01 certonly

## Q&A

1. 如果申请的通配符证书不包含主域名，再重新申请，会不会影响原先的证书使用？
  不会，原先证书仍可以正常使用。

## 参考

1. <a name='get_certbot'></a>[Get Certbot](https://certbot.eff.org/docs/install.html)
2. [申请Let's Encrypt通配符HTTPS证书](https://my.oschina.net/kimver/blog/1634575#comment-list)
3. [ywdblog/certbot-letencrypt-wildcardcertificates-alydns-au](https://github.com/ywdblog/certbot-letencrypt-wildcardcertificates-alydns-au)
4. [Let’s Encrypt通配符证书的申请与自动更新](http://blog.dreamlikes.cn/archives/1028)
5. [Certbot - Pre and Post Validation Hooks](https://certbot.eff.org/docs/using.html#pre-and-post-validation-hooks)
6. [阿里云 DNS API 文档](https://help.aliyun.com/document_detail/29740.html?spm=a2c4g.11186623.2.14.5c0a13b6y2tLom)

