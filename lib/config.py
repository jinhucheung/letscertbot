#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

config_path = os.path.sep.join([root_path, 'config.json'])

with open(config_path) as f:
    Config = json.load(f)

if __name__ == '__main__':
    print(Config)