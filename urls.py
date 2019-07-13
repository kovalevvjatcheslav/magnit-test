# -*- coding: utf-8 -*-
from views import view_comment, view_static, view_get_cities


urls = {
    'comment/': view_comment,
    'static/base.css': view_static,
    'static/base.js': view_static,
    'cities/': view_get_cities,
}
