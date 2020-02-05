# Let's Certbot

Let's Certbot 是一个基于 [Certbot](https://certbot.eff.org/) 用于自动化获取、续期、部署 SSL 证书的工具。

为了验证你的域名，Let's Certbot 使用了 Certbot 的 dns 方式进行验证。这对比 http 方式验证，你不需要在已部署的 Web 应用中进行任何操作，同时你也可以申请通配符证书。

在 dns 验证过程中，你需要为你的域名设置一个指定内容的 TXT DNS 记录。Let's Certbot 将会通过域名服务商的 DNS API 帮助你设置。

目前支持的域名服务商:

- [阿里云](https://www.aliyun.com/)
- [腾讯云](https://cloud.tencent.com/)
- [GoDaddy](https://godaddy.com)

## 安装

Let's Certbot 作为一个 Certbot 工具，支持 Docker 容器或非容器方式安装。

### 下载仓库

首先，克隆本仓库以获取 Let's Certbot:

```
$ git clone git@github.com:jinhucheung/letscertbot.git
```

然后拷贝配置文件:

```
$ cd letscertbot
$ cp config.json.example config.json
```

### 容器安装

你可以通过 Docker 来执行 Let's Certbot:

```
$ sudo docker run --rm --name letscertbot -v "$your_letscertbot_home/config.json:/app/config.json" -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" jimcheung/letscertbot
```

如果你已安装 Docker Compose, 可以通过 Compose 执行:

```
$ sudo docker-compose run --rm app
```

### 非容器安装

Let's Certbot 与 Certbot 执行环境一致，要求执行在类 UNIX 操作系统上且需要 Python 2.7 或 3.4+。

首先，你需要确认 Python 是否已经安装:

```
$ python --version
```

如果没有问题，根据 Certbot [官方文档](https://certbot.eff.org/docs/install.html) 为你的操作系统安装 Certbot。

在安装完 Certbot 后，使用 root 执行 Certbot:

```
$ sudo certbot --version
```

## 使用

### 配置

在执行 Let's Certbot 前，你有以下的配置需要更新:

| 名称                         | 必须  | 描述                                                               | 默认                  |
| ---------------------------- | ----- | ------------------------------------------------------------------ | --------------------- |
| base.email                   | true  | 邮箱地址，用于接收续期等通知                                       |                       |
| dns                          | true  | dns 设置                                                           |                       |
| dns.wait_time                | false | dns 验证等待时间(秒)                                               | 20                    |
| dns.aliyun.access_key_id     | false | 阿里云帐号的 AccessKey ID                                          |                       |
| dns.aliyun.access_key_secret | false | 阿里云帐号的 AccessKey Secret                                      |                       |
| dns.qcloud.secret_id         | false | 腾讯云帐号的 SecretId                                              |                       |
| dns.qcloud.secret_key        | false | 腾讯云帐号的 SecretKey                                             |                       |
| dns.godaddy.api_key          | false | GoDaddy 帐号的 API Key                                             |                       |
| dns.godaddy.api_secret       | false | GoDaddy 帐号的 API Secret                                          |                       |
| log.enable                   | false | 是否启用日志跟踪                                                   | false                 |
| log.logfile                  | false | 日志文件路径                                                       | ./log/application.log |
| deploy.servers               | false | 部署服务器列表                                                     |                       |
| deploy.server.enable         | false | 部署服务器是否启用部署脚本                                         | false                 |
| deploy.server.host           | false | 部署服务器地址，本地服务器则使用 localhost，启用部署脚本后必须提供 |                       |
| deploy.server.port           | false | 部署远程服务器 SSH 守护进程绑定的端口                              | 22                    |
| deploy.server.user           | false | 部署远程服务器登录的用户，用于执行部署脚本                         | root                  |
| deploy.server.password       | false | 部署远程服务器登录的密码                                           |                       |
| deploy.server.deploy_to      | false | 部署证书存储在服务器的路径                                         | /etc/letsencrypt/live |
| deploy.server.restart_nginx  | false | 是否在部署后重启服务器 nginx                                       | false                 |

此外， `tlds.txt` 文件包含了一些顶级域名(TLD)和二级域名(SLD) 用于分开域名中的子域和主域。如果你域名中的顶级域或二级域不在 `tlds.txt` 中，你需要将它添加在此文件中。

### DNS API

获取证书前，你可以执行 manual 脚本 (`manual.py`) 用你的 access key 测试 DNS API:

```
# 容器方式
$ sudo docker-compose run --rm app manual --test --domain your.example.com --dns aliyun

# 非容器方式
$ sudo python ./bin/manual.py --test --domain your.example.com --dns aliyun
```

这个脚本将会通过指定的 DNS API 添加 `_acme-challenge` TXT 记录到你的域名下。

### 获取证书

使用 root 执行 obtainment 脚本 (`obtain.py`) 以获取证书:

```
# 容器方式
$ sudo docker-compose run --rm app obtain -d your.example.com *.your.example.com

# 非容器方式
$ sudo python ./bin/obtain.py -d your.example.com *.your.example.com
```

然后你将在 `/etc/letsencrypt/live/` 目录下得到一个名为 `your.example.com` 通配符证书。

你可以提供 `--cert` 参数指定证书名称:

```
# 容器方式
$ sudo docker-compose run --rm app obtain -d x.example.com y.example.com --cert xny.example.com

# 非容器方式
$ sudo python ./bin/obtain.py -d x.example.com y.example.com --cert xny.example.com
```

### 续期证书

使用 renewal 脚本 (`renewal.py`) 为证书续期:

```
# 容器方式
$ sudo docker-compose run --rm app renewal

# 非容器方式
$ sudo python ./bin/renewal.py
```

Certbot 将为所有即将到期的证书续期。

你可以设置一个计划任务，将 renewal 脚本添加到 `crontab` 中:

```
# 容器方式
0 0 */7 * * sudo docker-compose -f $your_letscertbot_home/docker-compose.yml run --rm app renewal > /var/log/letscertbot-renewal.log 2>&1

# 非容器方式
0 0 */7 * * sudo $your_letscertbot_home/bin/renewal.py > /var/log/letscertbot-renewal.log 2>&1
```

这个计划任务将每 7 天执行 renewal 脚本。

如果你需要强制为指定的证书续期，可以提供 `--force` and `--certs` 参数:

```
# 容器方式
$ sudo docker-compose run --rm app renewal --certs xny.example.com --force

# 非容器方式
$ sudo python ./bin/renewal.py --certs xny.example.com --force
```

### 部署证书

如果你将 `deploy.server.enable` 设置为 true, Certbot 将执行 deployment 脚本 (`deploy.py`) 在 deploy 钩子上。这个脚本接收到已经续期的证书并将它推送到配置好的服务器中。

Let's Certbot 通过 SSH 为远程服务器部署证书，这意味着你执行 Certbot 的机器须通过 SSH 连接上远程服务器。为了使连接成功，你需要**上传公钥**到远程服务器或者**提供 `deploy.server.password`** 给 `sshpass` 工具。

此外，为了将证书部署到 `deploy.server.deploy_to` 或重启 nginx, Let's Certbot 要求 `deploy.server.user` 有执行对应操作的权限。

你可以通过执行下面命令获取 deployment 脚本:

```
# 容器方式
$ sudo docker-compose run --rm app deploy --check

# 非容器方式
$ sudo python ./bin/deploy.py --check
```

如果需要推送证书到配置中的服务器，可以执行:

```
# 容器方式
$ sudo docker-compose run --rm app deploy --push --cert $certificate_name --server $server_host

# 非容器方式
$ sudo python ./bin/deploy.py --push --cert $certificate_name --server $server_host
```

**Note**: 如果 `deploy.server` 以强制模式启动了 SELinux, 你需要确认 nginx 有权限访问 `deploy.server.deploy_to` 的 SELinux 安全上下文。

**Note**: 如果你以容器方式运行 Let's Certbot，同时需要在部署证书后重启本地 nginx 服务，则应该使用远程服务器方式配置本地服务器。

## 致谢

- [Certbot](https://github.com/certbot/certbot)
- [letsencrypt-aliyun-dns-manual-hook](https://github.com/broly8/letsencrypt-aliyun-dns-manual-hook)
- [certbot-letencrypt-wildcardcertificates-alydns-au](https://github.com/ywdblog/certbot-letencrypt-wildcardcertificates-alydns-au)

## 贡献

欢迎报告 Bug 或提交 Pull Request。

1. 分叉此仓库
2. 创建你的功能分支 (git checkout -b my-new-feature)
3. 提交你的改动 (git commit -am 'Add some feature')
4. 推送到当前分支 (git push origin my-new-feature)

如有必要，请为你的代码编写单元测试。

## 许可

根据 [MIT](MIT-LICENSE) 许可的条款，此仓库可作为开放源代码使用。