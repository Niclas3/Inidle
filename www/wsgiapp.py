# wsgiapp.py 
__author__ = 'niclas'

import logging; logging.basicConfig(level = logging.INFO)
import os

from datawarm import db
from datawarm.web import WSGIApplication, Jinja2TemplateEngine

from config import configs

# create databases
#db.create_engine(**configs.'db')
db.create_engine('root', '123', 'Inidle')

# create wsgiapp
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))

# init jinja2 engine
template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
    'templates'))
wsgi.template_engine = template_engine

# load @get/ @post URL functions
import urls
wsgi.add_module(urls)

# test in 9000
if __name__ == "__main__":
    wsgi.run(9000)
