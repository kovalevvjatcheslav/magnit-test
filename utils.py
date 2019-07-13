# -*- coding: utf-8 -*-
import os
import json
from context_managers import connection, get_cursor
from models import Region, City


def populate_db(db_name):
    exist_db = os.path.exists(db_name)
    with connection(db_name) as conn:
        with get_cursor(conn) as cursor:
            if not exist_db:
                with open('set_base.sql', 'rt') as set_base_script:
                    cursor.executescript(set_base_script.read())
        if not exist_db:
            with open('russian-subjects-master/native/regions.json', 'rt') as regions_json:
                regions = json.loads(regions_json.read())
            with open('russian-subjects-master/native/cities.json', 'rt') as cities_json:
                cities = json.loads(cities_json.read())
            for region_item in regions:
                region = Region(name=region_item['name'], db_conn=conn).save()
                for city_item in filter(lambda each: each['region_id'] == region_item['id'], cities):
                    City(name=city_item['name'], region=region, db_conn=conn).save()
