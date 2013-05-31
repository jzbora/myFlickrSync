#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide.QtCore import QUrl
from PySide.QtCore import Signal
from PySide.QtNetwork import QNetworkReply
from PySide.QtWebKit import QWebView
from flickr_api.auth import AuthHandler

OAUTH_URL = "http://www.flickr.com/services/oauth/authorize"

class FlickrAuthDialog(QWebView):

    signal_authFail = Signal(str)
    signal_authSuccess = Signal(str, str)

    def __init__(self, parent=None, auth_url=None):
        """
        Instantiate FlickrAuthDialog object.

        @param [parent] (QWidget)   Parent object that this widget belongs to.
        @param [key] (str)          FLickr App key
        @param [secret] (str)       FLickr App secret
        """

        super(FlickrAuthDialog, self).__init__(parent)

        self.load(auth_url)

        self.page()

        self._nam = self.page().networkAccessManager()

        # connect signals
        self.urlChanged.connect(self._slot_urlChanged)

    def _slot_urlChanged(self, url):
        """
        Slot for QWebView urlChanged signal.
        """
        fragment = url.fragment()
        path = url.path()
        query_items = dict(url.queryItems())

        if path == "/services/rest/":
            if "api_key" in query_items:
                access_token = query_items["api_key"]
            if "oauth_token" in query_items:
                oauth_token = query_items["oauth_token"]
            if "oauth_verifier" in query_items:
                oauth_verifier = query_items["oauth_verifier"]

            self.signal_authSuccess.emit(oauth_verifier, "success")
            return
        elif path == "/":
            self.signal_authFail.emit("fail")
