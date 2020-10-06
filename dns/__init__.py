#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dns.aliyun import Aliyun
from dns.qcloud import Qcloud
from dns.godaddy import GoDaddy
from dns.huaweicloud import HuaweiCloud
from dns.cloudflare import Cloudflare

types = {'aliyun', 'qcloud', 'godaddy', 'huaweicloud', 'cloudflare'}