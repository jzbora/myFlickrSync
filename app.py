#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import flickr_api
from PySide import QtGui, QtCore
from check import CheckThread
from auth_dialog import FlickrAuthDialog
import settings
from logger import logger
from utils import Utils

class UploadFrame(QtGui.QWidget):
    def __init__(self, model, flickr, parent=None):
        super(UploadFrame, self).__init__(parent)
        self.model = model
        self.flickr = flickr

        self.photos = []
        self.directory = None
        self.check_thread = None

        #self.setFixedSize(450,120)
        main_layout = QtGui.QGridLayout()
        
        self.edit_directory = QtGui.QLineEdit()
        self.edit_directory.setReadOnly(True)    
        self.edit_directory.setText(Utils.getConfig('directory'))
        self.edit_directory.setMaximumWidth(320)
        self.edit_directory.setMinimumWidth(320)
        if Utils.getConfig('directory'):
            self.directory = Utils.getConfig('directory')
        #button_directory.setMaximumWidth(290)
        self.button_browse = QtGui.QPushButton(self.tr("browse"))
        self.button_browse.setMaximumWidth(80)
        self.button_sync = QtGui.QPushButton(self.tr("sync"))
        self.button_sync.setMaximumWidth(80)
        
        self.button_browse.clicked.connect(self.browse)
        self.button_sync.clicked.connect(self.startUploadThread)

        self.button_more = QtGui.QCheckBox(self.tr('more'))

        extension = QtGui.QWidget()

        self.button_delete_db = QtGui.QPushButton("clean")
        self.button_delete_db.clicked.connect(self.deleteDB)

        button_delete_auth = QtGui.QPushButton("unlink")
        button_delete_auth.clicked.connect(self.deleteAuth)

        self.button_more.toggled.connect(extension.setVisible)

        extensionLayout = QtGui.QHBoxLayout()
        extensionLayout.setContentsMargins(0, 0, 0, 0)
        extensionLayout.addWidget(self.button_delete_db)
        extensionLayout.addWidget(button_delete_auth)
        extension.setLayout(extensionLayout)

        main_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        main_layout.addWidget(self.edit_directory, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        main_layout.addWidget(self.button_browse, 0, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)
        main_layout.addWidget(self.button_sync, 1, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        main_layout.addWidget(self.button_more, 2, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        main_layout.addWidget(extension, 3, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)
        
        self.setLayout(main_layout)
        extension.hide()

    def browse(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, self.tr("find photos files"))
        if directory:
            self.edit_directory.setText(directory)      
            self.directory = directory
            Utils.setConfig("directory", directory)

    def startUploadThread(self):
        if self.directory:
            self.button_browse.setEnabled(False)
            self.button_sync.setEnabled(False)
            self.button_delete_db.setEnabled(False)            
            self.check_thread = CheckThread(self, self.flickr, self.directory)
            self.check_thread.start()

    def finishUploadThread(self):
        self.button_browse.setEnabled(True)
        self.button_sync.setEnabled(True)
        self.button_delete_db.setEnabled(True)            

    def deleteAuth(self):
        Utils.deleteAuth()
        sys.exit()

    def deleteDB(self):
        Utils.deleteDB()

class AuthFrame(QtGui.QWidget):
    def __init__(self, model, flickr, parent=None):
        super(AuthFrame, self).__init__(parent)

        self.setFixedSize(800,600)

        self.setWindowTitle(self.tr('flickr login'))
        FLICKR_APP_KEY = getattr(settings, 'FLICKR_APP_KEY')
        FLICKR_APP_SECRET = getattr(settings, 'FLICKR_APP_SECRET')

        self.model = model

        self.flickr = flickr
        self.flickr.set_keys(api_key = FLICKR_APP_KEY, api_secret = FLICKR_APP_SECRET)
        self.auth = self.flickr.auth.AuthHandler()
        auth_url = self.auth.get_authorization_url("write")

        self.flickr_auth = FlickrAuthDialog(parent = self, auth_url = auth_url)

        self.flickr_auth.signal_authSuccess.connect(self._slot_authSuccess)
        self.flickr_auth.signal_authFail.connect(self._slot_authFail)

    def save(self, oauth_verifier):
        auth_path = getattr(settings, 'AUTH_PATH')
        self.auth.set_verifier(oauth_verifier)
        self.flickr.set_auth_handler(self.auth)
        self.auth.save(auth_path)

    def _slot_authSuccess(self, oauth_code, state):
        logger.info("_slot_authSuccess")
        logger.info("oauth_code %s" %oauth_code)
        logger.info("state %s" %state)
        self.save(oauth_code)
        self.hide()
        self.upload_frame = UploadFrame(self, self.flickr)
        self.upload_frame.show()

    def _slot_authFail(self, state):
        logger.info("_slot_authFail")
        logger.info("state %s" %state)
        self.close()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    Utils.createDB()
    FLICKR_APP_KEY = getattr(settings, 'FLICKR_APP_KEY')
    FLICKR_APP_SECRET = getattr(settings, 'FLICKR_APP_SECRET')
    flickr_api.set_keys(api_key = FLICKR_APP_KEY, api_secret = FLICKR_APP_SECRET)
    auth_path = getattr(settings, 'AUTH_PATH')
    if os.path.exists(auth_path):
        auth = flickr_api.auth.AuthHandler.load(auth_path)
        flickr_api.set_auth_handler(auth)
    try:
        user = flickr_api.test.login()
    except flickr_api.flickrerrors.FlickrAPIError:
        logger.info("Errro")
        auth_frame = AuthFrame(None, flickr_api)
        auth_frame.show()
    else:
        logger.info(user)
        upload_frame = UploadFrame(None, flickr_api)
        upload_frame.show()
    sys.exit(app.exec_())