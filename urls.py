# -*- coding: utf-8 -*-
from views import view_add_comment, view_static, view_get_cities, view_comments, view_stat, view_region


urls = {
    'comment/': view_add_comment,
    'static/base.css': view_static,
    'static/base.js': view_static,
    'cities/': view_get_cities,
    'view/': view_comments,
    'stat/': view_stat,
    'region/': view_region,
}
