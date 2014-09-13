#-*- coding:utf8 -*-

__author__ = 'niclas'

from datawarm.web import get, view, ctx, view, interceptor, seeother, notfound, post
from models import Users, Plans
from datawarm import db
from apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
import os, re, time, base64, hashlib, logging

#db.create_engine('root', '123', 'Inidle')

@view('test.html')
@get('/test')
def test_users():
    users = Users.find_all()
    return dict(users=users)

@view('index.html')
@get('/index')
def index():
    users = Users.find_first('where user_id=?', '3')
    return dict(users=users)

@view('register.html')
@get('/register')
def register():
    return dict()

@view('signin.html')
@get('/signin')
def login():
    return dict()

@view('__base__.html')
@get('/')
def xxx():
    return dict()


_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')
# write API
@api
@post('/api/users')
def resgister_usr():
    print 'use this'
    i = ctx.request.input(name='', password='')
    name = i.name.strip()
    password = i.password
    if not name:
        raise APIValueError('name')
    if not password: #or not _RE_MD5.match(password):
        raise APIValueError('password')
    if user:
        raise APIError('register:failed')
    user = User(user_name=name, user_pass=password)
    user.insert()
    return user

