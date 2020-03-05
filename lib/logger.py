#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

from .config import Config

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

if Config['log'].get('enable', False):
    logfile = Config['log'].get('logfile', None) or './log/application.log'
    if not logfile.startswith('/'):
        logfile = os.path.sep.join([root_path, logfile])

    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=logging.DEBUG,
        filename=logfile,
        filemode='a'
    )
else:
    logging.basicConfig()

Logger = logging.getLogger('logger')