# -*- coding: utf-8 -*-


def view_404(environ, start_response):
    with open('html/404.html', 'rt') as response:
        start_response('404 Not Found,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read()


def view_comment(environ, start_response):
    with open('html/comment.html', 'rt') as response:
        start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read()
