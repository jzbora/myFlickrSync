#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import logging
import settings

# logging setup
logger = logging.getLogger('mySync')
logger.setLevel(logging.DEBUG)
LOG_PATH = getattr(settings, 'LOG_PATH')
logFile = os.path.join(LOG_PATH, 'mysync.log')
handler = logging.FileHandler(logFile)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#logger.addHandler(logging.StreamHandler())
