''' Functionality for processing requests to the CADBase platform '''

import json
import pathlib
from PySide import QtCore  # FreeCAD's PySide
from PySide2 import QtNetwork
import FreeCAD as app
from CadbaseLibrary.CdbsEvn import g_param, g_content_type, g_response_path
import CadbaseLibrary.DataHandler as DataHandler
from CadbaseLibrary.DataHandler import logger

class CdbsApi:
    ''' class for sending requests and handling responses '''

    def __init__(self, query):
        logger(3, 'Getting data...')
        self.do_request(query)

    def do_request(self, query):
        api_url = g_param.GetString('api-url', '')
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(api_url))

        auth_header = 'Bearer ' + g_param.GetString('auth-token', '')
        header = {'Authorization': auth_header}

        req.setRawHeader(b'Content-Type', g_content_type);
        req.setRawHeader(b'Authorization', auth_header.encode());

        body = json.dumps(query).encode('utf-8')

        self.nam = QtNetwork.QNetworkAccessManager()
        reply = self.nam.post(req, body)
        loop = QtCore.QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec_()
        self.handle_response(reply)

    def handle_response(self, reply):
        DataHandler.remove_object(g_response_path) # deleting old a response if it exists
        er = reply.error()

        if er == QtNetwork.QNetworkReply.NoError:
            if reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute) == 200:
                response_bytes = reply.readAll()
                with g_response_path.open('wb') as file:
                    file.write(response_bytes)
                logger(3, 'Success')
            else:
                logger(1, f'Failed, status code: {reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)}')
        else:
            logger(1, f'Error occured: {er}')
            logger(1, f'{reply.errorString()}')
