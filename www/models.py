# -*- coding:utf8 -*-
__author__ = 'Niclas'

'''
Models for Users, Plans, Config.
'''

from datawarm.ORM import Model, IntegerField,\
        StringField, BooleanField, FloatField, TextField, VersionField, BlobField

class Users(Model):
    __table__ = 'Users'

    user_id           = IntegerField(primary_key=True, ddl='int')
    user_name         = StringField(ddl='varchar(15)')
    user_pass         = StringField(ddl='varchar(15)')
    user_icon         = BlobField(ddl='MEDIUMBLOB')
    user_isdel        = BooleanField(ddl='boolean', default=0)
    user_delTime      = FloatField(updatable=False)
    user_friendsNum   = IntegerField(default=0)
    user_friendsNames = TextField()


class Plans(Model):
    __table__ = 'Plans'

    plan_id          = IntegerField(primary_key=True, ddl='int')
    plan_userId      = IntegerField(updatable=False, ddl='int')
    plan_classId     = IntegerField(updatable=False,ddl='int')
    plan_monthvector = IntegerField(ddl='int')
    plan_dayvector   = IntegerField(ddl='int')
    plan_gemTime     = FloatField(updatable=False)


class Config(Model):
    __table__ = 'Config'

    config_id     = IntegerField(primary_key=True, ddl='int')
    config_userid = IntegerField(updatable=False, ddl='int')
    is_visible    = BooleanField(default=0)


