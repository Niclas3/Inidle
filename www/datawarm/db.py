# -*- coding:utf-8 -*-

__author__ = 'Niclas'

'''
Database operation module
'''

import time, uuid, functools, threading, logging

# tools with tuple => dict
class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class DBError(Exception):
    pass


class MultiColumnsError(DBError):
    pass


class _AutoConnection(object):
    '''
    use this class to autoconnect database without care about
    close or craete connection in upper level code.
    '''

    def __init__(self):
        self.connection = None
    
    def cursor(self):
        if self.connection is None:
            connection  = engine.connect()
            logging.info('open connection <%s>..' % hex(id(connection)))
            self.connection = connection
        return self.connection.cursor()

    def commit(self):
        if self.connection is None:
            logging.info('Connection is lose...')
        return self.connection.commit()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()

    def rollback(self):
        self.connection.rollback()


class _DbCtx(threading.local):
    '''
    Use threading local object to hold connection info.
    '''
    def __init__(self):
        self.connection = None
        self.transaction = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        self.connection = _AutoConnection()
        self.transaction = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        '''
        return a cursor
        '''
        return self.connection.cursor()


# thread-Local db context:
_db_ctx = _DbCtx()

# glabal engine object:
engine = None

class _Engine(object):
    '''
    Engine is a connection with Mysql
    like that 
    import mysql
    config = {config={'host':'127.0.0.1',
        'user':'root',
        'password':'123456',
        'port':3306 ,
        'database':'test',  
        'charset':'utf8'
        }
    cnn = mysql.connector.connect(**config)
    '''

    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    import mysql.connector  # only use one time
    global engine
    if engine is not None:
        raise DBError("Engine is already initialized.")

    params = dict(user=user, password=password,
            database=database, host=host, port=port)
    defaults = dict(use_unicode=True, 
            charset='utf8', collation='utf8_general_ci', autocommit=False)

    for key, value in defaults.iteritems():
        params[key] = kw.pop(key, value)
    params.update(kw)
    params['buffered'] = True

    engine = _Engine(lambda : mysql.connector.connect(**params))

    logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

class _ConnectionCtx(object):
    
    def __enter__(self):
        global _db_ctx

        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True

        return self
    
    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        logging.info('commit sql stmt...')
        try:
            _db_ctx.connection.commit()
            logging.info('commit ok.')
        except:
            logging.waring('commit faild. try rollback...')

def connection():
    '''
    Return _ConnectionCtx object and can be used by 'with' statement
    '''
    return _ConnectionCtx()

def with_connection(func):
    '''
    Decorator for reuse connection.
    
    '''
    @functools.wraps(func)
    def _wrapper(*arg, **kw):
        with _ConnectionCtx():
            return func(*arg, **kw)
    return _wrapper

def _select(sql, frist, *args):
    ' execute select SQL and return unique result or list results.'
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL:%s, ARGS: %s' % (sql, args))

    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if frist:
            values = cursor.fetchone;
            if not values:
                return None
            return Dict(names, values)  # return diction type 
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()

@with_connection
def select_one(sql, *args):
    '''
    Execute select SQL and expected one result. 
    If no result found, return None.
    If multiple results found, the first one returned.

    >>> u1 = dict(id=100, name='Alice', email='alice@test.org', passwd='ABC-12345', last_modified=time.time())
    >>> u2 = dict(id=101, name='Sarah', email='sarah@test.org', passwd='ABC-12345', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> insert('user', **u2)
    1
    >>> u = select_one('select * from user where id=?', 100)
    >>> u.name
    u'Alice'
    >>> select_one('select * from user where email=?', 'abc@email.com')
    >>> u2 = select_one('select * from user where passwd=? order by email', 'ABC-12345')
    >>> u2.name
    u'Alice'
    '''
    return _select(sql, True, *args)

@with_connection
def select_int(sql, *args):
    '''
    Execute select SQL and expected one int and only one int result. 

    >>> n = update('delete from user')
    >>> u1 = dict(id=96900, name='Ada', email='ada@test.org', passwd='A-12345', last_modified=time.time())
    >>> u2 = dict(id=96901, name='Adam', email='adam@test.org', passwd='A-12345', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> insert('user', **u2)
    1
    >>> select_int('select count(*) from user')
    2
    >>> select_int('select count(*) from user where email=?', 'ada@test.org')
    1
    >>> select_int('select count(*) from user where email=?', 'notexist@test.org')
    0
    >>> select_int('select id from user where email=?', 'ada@test.org')
    96900
    >>> select_int('select id, name from user where email=?', 'ada@test.org')
    Traceback (most recent call last):
        ...
    MultiColumnsError: Expect only one column.
    '''
    d = _select(sql, True, *args)
    if len(d)!=1:
        raise MultiColumnsError('Expect only one column.')
    return d.values()[0]

@with_connection
def select(sql, *args):
    '''
    Execute select SQL and return list or empty list if no result.

    >>> u1 = dict(id=200, name='Wall.E', email='wall.e@test.org', passwd='back-to-earth', last_modified=time.time())
    >>> u2 = dict(id=201, name='Eva', email='eva@test.org', passwd='back-to-earth', last_modified=time.time())
    >>> insert('user', **u1)
    1
    >>> insert('user', **u2)
    1
    >>> L = select('select * from user where id=?', 900900900)
    >>> L
    []
    >>> L = select('select * from user where id=?', 200)
    >>> L[0].email
    u'wall.e@test.org'
    >>> L = select('select * from user where passwd=? order by id desc', 'back-to-earth')
    >>> L[0].name
    u'Eva'
    >>> L[1].name
    u'Wall.E'
    '''
    return _select(sql, False, *args)

@with_connection
def _update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?','%s')
    logging.info("SQL: %s ARGS: %s" % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transaction == 0:
            logging.info('auto commit')
            _db_ctx.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()

def insert(table, **kw):
    pass

def update(sql, *args):
    return _update(sql, *args)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info('start DEBUG')
    create_engine('root','123', 'inidle')
    L = select('select count(*) from Users')
    print L
