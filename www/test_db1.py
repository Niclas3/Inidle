# test DB

from models import Users, Plans, Config
from datawarm import db

db.create_engine('root','123','Inidle')

u = Users.find_first('where user_id=?', '3')
print u.user_name

u = Users(user_name='Tom', user_pass='12345',is_del=False)

u1 = Users.find_by("where user_name=? and user_pass=?", 'Tom', '12345')
u1.delete()
print u1

