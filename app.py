# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server
from wsgiref.validate import validator
from wsgiref.util import application_uri, request_uri
from urls import urls
from views import view_404


def app(environ, start_response):
    uri = request_uri(environ, include_query=False).replace(application_uri(environ), '')
    yield urls.get(uri, view_404)(environ, start_response).encode('utf-8')


if __name__ == '__main__':
    with make_server('', 8080, validator(app)) as server:
        server.serve_forever()
