# -*- coding:utf8 -*-
import functools
import db

db.create_engine('root', '123', 'Inidle')
property
#r=db.select('select * from Users')

r = db.select('select user_name, user_pass from Users')

x = ('name', 'vlaue','t')
y = (2, 3, 4)

xy = zip(x, y)
print zip(*xy)
