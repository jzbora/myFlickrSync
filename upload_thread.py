#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
from PySide import QtGui, QtCore
import settings
from logger import logger
import urllib2, mimetools, mimetypes
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from xml.etree import ElementTree as ET
from flickr_api.flickrerrors import FlickrError, FlickrAPIError
from flickr_api.objects import Photo, UploadTicket, Photoset
import flickr_api
from utils import Utils
import datetime

class UploadThread(QtCore.QObject):
    def __init__(self, model, flickr, filepath, photoset, parent=None):
        super(UploadThread, self).__init__(parent)
        self.model = model
        self.flickr = flickr
        self.auth_handler = flickr.auth.AUTH_HANDLER
        self.filepath = filepath
        self.photoset = photoset
        self.photoset_txt = photoset

    def check(self):
        logger.info("start upload %s" %self.filepath)
        photh = None
        photoset_exist = False
        url = getattr(settings, 'UPLOAD_URL')
        user = flickr_api.test.login()
        photosets = user.getPhotosets()

        #check photoset
        for photoset in photosets:
            if photoset['title'] == self.photoset:
                self.photoset = photoset
                photoset_exist = True
                break

        name, ext = os.path.splitext(os.path.basename(self.filepath))
        args = {'title': name.encode("utf-8")}
        params = self.auth_handler.complete_parameters(url,args).parameters
        params['photo'] = open(self.filepath, "rb")
        register_openers()
        datagen, headers = multipart_encode(params)
        request = urllib2.Request(url, datagen, headers)
        result = urllib2.urlopen(request)

        upload_date = datetime.datetime.now()

        if result.getcode() != 200 :
            Utils.insertDB(self.filepath, self.photoset_txt, 0, upload_date)
            raise FlickrError("HTTP Error %i: %s"%(r.status,r.read()))
        content = ET.fromstring(result.read())
        if content.get("stat")!= 'ok' :
            err = content[0]
            Utils.insertDB(self.filepath, self.photoset_txt, 0, upload_date)            
            raise FlickrAPIError(int(err.get("code")),err.get("msg"))
        else:
            t = content[0]
            if t.tag == 'photoid' :
                logger.info(t.text)
                photo = Photo(id = t.text, editurl='http://www.flickr.com/photos/upload/edit/?ids=' + t.text)
            elif t.tag == 'ticketid' :
                pass
            else :
                raise FlickrError("Unexpected tag: %s"%t.tag)
        if photo and self.photoset:
            if photoset_exist:
                self.photoset.addPhoto(photo = photo)
            else:
                self.photoset = Photoset.create(title = self.photoset.encode("utf-8"), primary_photo = photo)

        Utils.insertDB(self.filepath, self.photoset_txt, 1, upload_date)
        #logger.info(photoset)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    filepath = "test//bb.jpg"
    photoset = ""

    FLICKR_APP_KEY = getattr(settings, 'FLICKR_APP_KEY')
    FLICKR_APP_SECRET = getattr(settings, 'FLICKR_APP_SECRET')

    flickr_api.set_keys(api_key = FLICKR_APP_KEY, api_secret = FLICKR_APP_SECRET)

    auth_path = getattr(settings, 'AUTH_PATH')

    auth = flickr_api.auth.AuthHandler.load(auth_path)
    flickr_api.set_auth_handler(auth)
    logger.info(flickr_api.auth.AUTH_HANDLER)
    upload_thread = UploadThread(None, flickr_api, filepath, photoset)
    upload_thread.check()
    sys.exit(app.exec_())