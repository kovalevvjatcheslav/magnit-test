# -*- coding: utf-8 -*-
from wsgiref.util import application_uri, request_uri
import json
from html import escape
from urllib.parse import parse_qs
from models import Region, City, Comment
from context_managers import connection, get_cursor
from settigs import DB_NAME


def view_404(environ, start_response):
    with open('html/404.html', 'rt') as response:
        start_response('404 Not Found,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read()


def view_add_comment(environ, start_response):
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
        with open('html/region_option.html', 'rt') as region_template:
            region_template_str = region_template.read()
        regions = '\n'.join((region_template_str.replace('{id}', str(region.id)).replace('{name}', region.name)
                             for region in Region.get_all(conn)))
    with open('html/add_comment.html', 'rt') as response:
        start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
        return response.read().replace('{regions}', regions)


def view_static(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'get':
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


def view_comments(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'get':
        with connection(DB_NAME) as conn:
            with open('html/comment.html', 'rt') as comment_template:
                comment_template_str = comment_template.read()
            comments = '\n'.join(comment_template_str.replace('{surname}', comment.surname).replace('{name}', comment.name)
                                 .replace('{patronymic}', comment.patronymic if comment.patronymic else '')
                                 .replace('{region_name}', comment.city.region.name if comment.city else '')
                                 .replace('{city_name}', comment.city.name if comment.city else '')
                                 .replace('{phone}', comment.phone if comment.phone else '')
                                 .replace('{email}', comment.email if comment.email else '')
                                 .replace('{comment}', comment.comment)
                                 .replace('{id}', str(comment.id))
                                 for comment in Comment.get_all(conn))
        with open('html/view.html', 'rt') as response:
            start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
            return response.read().replace('{comments}', comments)
    elif environ['REQUEST_METHOD'].lower() == 'post':
        with connection(DB_NAME) as conn:
            params = json.loads(environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))).decode('utf-8'))
            comment_id = int(params.get('commentId'))
            Comment.remove_by_id(comment_id, conn)
            start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
            return '123'


def view_stat(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'get':
        with connection(DB_NAME) as conn:
            with open('html/region_comment.html', 'rt') as stat_rows_template:
                stat_rows_template_str = stat_rows_template.read()
            with get_cursor(conn) as cur:
                regions_ids = cur.execute('''select region_id from City 
                                             where id in (select city_id from Comment 
                                                          group by city_id having count(*)>5);''').fetchall()
            regions_ids = set(region_id[0] for region_id in regions_ids)
            comments_count = {region_id: len(tuple(Comment.get_by_region_id(region_id, conn))) for region_id in regions_ids}
            stat_rows = '\n'.join(stat_rows_template_str.replace('{region_id}', str(region_id))
                                  .replace('{name}', Region.get_by_id(region_id, conn).name)
                                  .replace('{comments_count}', str(comments_count[region_id]))
                                  for region_id in regions_ids)
            with open('html/stat.html', 'rt') as response:
                start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
                return response.read().replace('{rows}', stat_rows)


def view_region(environ, start_response):
    if environ['REQUEST_METHOD'].lower() == 'get':
        region_id = int(parse_qs(environ['QUERY_STRING']).get('regionId')[0])
        with connection(DB_NAME) as db_conn:
            region = Region.get_by_id(region_id, db_conn)
            cities = City.get_by_region_id(region_id, db_conn)
            with open('html/city.html', 'rt') as city_rows_template:
                city_rows_template_str = city_rows_template.read()
            city_rows = '\n'.join(city_rows_template_str.replace('{city_name}', city.name) for city in cities)
        with open('html/region_view.html', 'rt') as response:
            start_response('200 OK,', [('Content-Type', 'text/html; charset=UTF-8')])
            return response.read().replace('{region_name}', region.name).replace('{city_rows}', city_rows)
