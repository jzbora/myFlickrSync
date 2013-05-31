#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
from PySide import QtGui, QtCore
import settings
import flickr_api
from upload_thread import UploadThread
from logger import logger
from utils import Utils

class CheckThread(QtCore.QThread):
    def __init__(self, model, flickr, directory, parent=None):
        super(CheckThread, self).__init__(parent)
        logger.info("init check thread")
        self.model = model
        self.flickr = flickr
        self.directory = directory
        self.photos = []
        self.upload_thread = None

    def run(self):
        temp = ''
        SUPPORT_FORMATS = getattr(settings, 'SUPPORT_FORMATS')
        if os.path.isdir(self.directory):
            for root, dirs, files in os.walk(self.directory):
                #logger.info(dirs)
                for filename in files:
                    name, ext = os.path.splitext(filename)
                    if ext.lower() in SUPPORT_FORMATS:
                        filepath = os.path.join(root, filename)
                        if not Utils.checkDB(filepath):
                            if root != self.directory:
                                temp = os.path.basename(root)
                                self.photos.append([temp, filepath])
                            else:
                                self.photos.append(["", filepath])

        for photoset, photo in self.photos:
            self.upload_thread = UploadThread(self, self.flickr, photo, photoset)
            self.upload_thread.check()

        self.model.finishUploadThread()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    FLICKR_APP_KEY = getattr(settings, 'FLICKR_APP_KEY')
    FLICKR_APP_SECRET = getattr(settings, 'FLICKR_APP_SECRET')

    flickr_api.set_keys(api_key = FLICKR_APP_KEY, api_secret = FLICKR_APP_SECRET)

    auth_path = getattr(settings, 'AUTH_PATH')

    auth = flickr_api.auth.AuthHandler.load(auth_path)
    flickr_api.set_auth_handler(auth)
    logger.info(flickr_api.auth.AUTH_HANDLER)
    directory = u"C:\\Temp\\test"
    check_thread = CheckThread(None, flickr_api, directory)
    check_thread.start()
    sys.exit(app.exec_())    