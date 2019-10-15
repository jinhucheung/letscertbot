#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

if sys.version_info < (3,0):
    import ConfigParser
else:
    import configparser as ConfigParser

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

config_path = os.path.sep.join([root_path, 'config.ini'])

Config = ConfigParser.ConfigParser()
Config.read(config_path)