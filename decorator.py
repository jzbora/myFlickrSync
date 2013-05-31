#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from time import sleep
import logging
import sqlite3

# logging setup
logger = logging.getLogger('liuda')

def log_info(func):
    def wrapper(*args, **kws):
        logger.info('start %s' %func.func_name)
        res = func(*args, **kws)
        logger.info('end %s' %func.__name__)
        return res
    return wrapper

def db_locked_retry(howmany):
    def tryIt(func):
        def wrapper(*args, **kws):
            ignore_func = ("checkDB", )
            attempts = 0
            run_flag = True
            res = None
            while True:
                if attempts < howmany:
                    try:
                        res = func(*args, **kws)
                    except sqlite3.OperationalError as e:
                        ee = str(e)
                        if ee == "database is locked":
                            logger.info("database is locked, attempts %s" %attempts)
                            attempts += 1
                            sleep(0.5)
                            continue
                        else:
                            logger.info("other error")
                    else:
                        func_name = func.func_name
                        if func_name not in ignore_func:
                            logger.info("%s success" %func_name)
                else:
                    logger.info("max attempts")
                return res
        return wrapper
    return tryIt