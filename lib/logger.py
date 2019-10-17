#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

from .config import Config

root_path = os.path.sep.join([os.path.split(os.path.realpath(__file__))[0], '..'])

Logger = logging.getLogger('logger')

if 'enable' in Config['log'] and Config['log']['enable']:
    logfile = Config['log']['logfile'] if 'logfile' in Config['log'] and Config['log']['logfile'] else './log/application.log'
    if not logfile.startswith('/'):
        logfile = os.path.sep.join([root_path, logfile])

    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=logging.DEBUG,
        filename=logfile,
        filemode='a'
    )
