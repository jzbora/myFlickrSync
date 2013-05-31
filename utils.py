#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import sqlite3
from PySide import QtCore
from logger import logger
from sys import platform
import settings

class Utils(QtCore.QObject):
    @classmethod
    def setConfig(cls, key, value):
        """ set config """
        settings = QtCore.QSettings("myFlickr", "mySync")
        settings.setValue(key, value)
    
    @classmethod 
    def getConfig(cls, key):
        """ get config """
        settings = QtCore.QSettings("myFlickr", "mySync")
        if key=='directory':
            if not settings.value('directory'):
                cls.setConfig('directory', '')
            if not os.path.exists(settings.value('directory')):
                return ''
        return settings.value(key)

    @classmethod    
    def dataDir(cls):
        """ get data file directory """
        if platform == 'win32':        
            import winpaths
            path = winpaths.get_common_appdata()
            path = os.path.join(path, 'mySync')
            if not os.path.isdir(path): os.mkdir(path)
        elif platform == 'darwin':
            user_path = os.path.expanduser('~') 
            path = os.path.join(user_path, 'Library')
            if not os.path.isdir(path): os.mkdir(path)
            path = os.path.join(path, 'Application Support')
            if not os.path.isdir(path): os.mkdir(path)
            path = os.path.join(path, 'mySync')
            if not os.path.isdir(path): os.mkdir(path)
        else:
            path = cls.curFileDir()
        return path

    @classmethod
    def sqlDir(cls):
        """ get database file """
        return os.path.join(cls.dataDir(), 'photos.db')

    @classmethod
    def createDB(cls):
        """ create database and photo table """
        logger.info(cls.sqlDir())
        conn = sqlite3.connect(cls.sqlDir())
        sql_create = '''CREATE TABLE "photos" (
        "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "name"  varchar,
        "photoset" varchar,
        "status"  smallint,
        "file"  varchar,
        "upload_date"  date
        )''' 
        try:
            conn.execute(sql_create)
        except sqlite3.OperationalError:
            pass
            #logger.info('db fail')
        else:
            conn.commit()
        conn.close()
        logger.info('db ok')

    @classmethod
    def checkDB(cls, filepath):
        """ check whether the file """
        conn = sqlite3.connect(cls.sqlDir(), timeout=3)
        cur = conn.cursor()
        res = None     
        sql_check = "select count(0) from photos where file=? and status=1"
        cur.execute(sql_check, [filepath, ])
        res = cur.fetchone()
        conn.close()
        if res[0] <= 0:
            return False
        else:
            logger.info('%s exist on line' % filepath)
            return True

    @classmethod
    def insertDB(cls, file, photoset, status, upload_date):
        """ insert success photo info """
        name = os.path.basename(file)

        conn = sqlite3.connect(cls.sqlDir(), timeout=3)
        cur = conn.cursor()
        sql_check = "select count(0) from photos where file=?"
        cur.execute(sql_check, [file])
        conn.commit()
        res = cur.fetchone()   
        if res[0] <=0:
            upload_date = upload_date
            sql = '''
                insert into photos
                (name, photoset, status, file, upload_date) 
                values
                (?, ?, ?, ?, ?)
                ''' 
            conn.execute(sql, 
                    [name, photoset, status, file, upload_date]
                )
        else:
            sql = "update photos set status=? where file=?" 
            conn.execute(sql, [status, upload_date])
        conn.commit()             
        conn.close()
        logger.info("insert db %s" %file)

    @classmethod
    def deleteDB(cls):
        """ delete database """
        if os.path.exists(cls.sqlDir()):
            os.remove(cls.sqlDir())

    @classmethod
    def deleteAuth(cls):
        """ delete auth """
        auth_path = getattr(settings, 'AUTH_PATH')
        if os.path.exists(auth_path):
            os.remove(auth_path)