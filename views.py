# -*- coding: utf-8 -*-
from wsgiref.util import application_uri, request_uri
import json
from html import escape
from models import Region, City
from context_managers import connection
from settigs import DB_NAME


def view_404(environ, start_response):
    with open('html/404.html', 'rt') as response:
        start_response('404 Not Found,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read()


def view_comment(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'get':
        with connection(DB_NAME) as conn:
            with open('html/region.html') as region_template:
                region_template_str = region_template.read()
            regions = '\n'.join((region_template_str.replace('{id}', str(region.id)).replace('{name}', region.name)
                                 for region in Region.get_all(conn)))
        with open('html/comment.html', 'rt') as response:
            start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
            return response.read().replace('{regions}', regions)
    elif environ['REQUEST_METHOD'].lower() == 'post':
        start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
        return 'шиш'


def view_static(environ, start_response):
    uri = request_uri(environ, include_query=False).replace(application_uri(environ), '')
    start_response('200 OK,', [('Content-Type', f'text/{uri.split(".")[1]}')])
    with open(uri, 'rt') as response:
        return response.read()


def view_get_cities(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'post':
        params = json.loads(environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))))
        region_id = params.get('region_id')
        with connection(DB_NAME) as db_conn:
            cities = json.dumps(
                [{'cityId': city.id, 'cityName': city.name} for city in City.get_by_region_id(region_id, db_conn)]
            )
        start_response('200 OK,', [('Content-Type', 'application/json; charset=UTF-8')])
        return cities
