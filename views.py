# -*- coding: utf-8 -*-
from wsgiref.util import application_uri, request_uri
import json
from html import escape
from urllib.parse import parse_qs
from models import Region, City, Comment
from context_managers import connection
from settigs import DB_NAME


def view_404(environ, start_response):
    with open('html/404.html', 'rt') as response:
        start_response('404 Not Found,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read()


def view_comment(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'post':
        params = parse_qs(environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))).decode('utf-8'))
        surname = escape(params.get('surname', [''])[0])
        name = escape(params.get('name', [''])[0])
        patronymic = escape(params.get('patronymic', [''])[0])
        city_id = int(escape(params.get('cityId', ['0'])[0]))
        phone = escape(params.get('phone', [''])[0])
        email = escape(params.get('email', [''])[0])
        comment_text = escape(params.get('comment', [''])[0])
        with connection(DB_NAME) as conn:
            city = City.get_by_id(id=city_id, db_conn=conn)
            Comment(name=name, surname=surname, comment=comment_text, db_conn=conn, patronymic=patronymic, city=city,
                    phone=phone, email=email).save()
    with connection(DB_NAME) as conn:
        with open('html/region.html') as region_template:
            region_template_str = region_template.read()
        regions = '\n'.join((region_template_str.replace('{id}', str(region.id)).replace('{name}', region.name)
                             for region in Region.get_all(conn)))
    with open('html/comment.html', 'rt') as response:
        start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read().replace('{regions}', regions)


def view_static(environ, start_response):
    uri = request_uri(environ, include_query=False).replace(application_uri(environ), '')
    start_response('200 OK,', [('Content-Type', f'text/{uri.split(".")[1]}')])
    with open(uri, 'rt') as response:
        return response.read()


def view_get_cities(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'get':
        region_id = int(parse_qs(environ['QUERY_STRING']).get('regionId')[0])
        with connection(DB_NAME) as db_conn:
            cities = json.dumps(
                [{'cityId': city.id, 'cityName': city.name} for city in City.get_by_region_id(region_id, db_conn)]
            )
        start_response('200 OK,', [('Content-Type', 'application/json; charset=UTF-8')])
        return cities
