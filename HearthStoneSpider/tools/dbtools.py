# -*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
from DBUtils.PooledDB import PooledDB

class MySQLdbHelper:
    def __init__(self):
        # 启动时连接池中创建的的连接数
        # 'mincached': 5,
        # 连接池中最大允许创建的连接数
        # 'maxcached': 20,
        conn_args = {
            'host': '47.98.187.217',
            'db': 'hearthstonestation',
            'user': 'root',
            'password': '666666',
            'charset': 'utf8',
            'cursorclass': MySQLdb.cursors.DictCursor
        }
        self._pool = PooledDB(MySQLdb, mincached=5, maxcached=20, **conn_args)

    def getConn(self):
        conn = self._pool.connection()
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("set names utf8mb4;")
        cursor.close()
        return conn

class DBManager(object):
    def __init__(self):
        try:
            self.conn = MySQLdbHelper().getConn()
        except MySQLdb.DatabaseError as e:
            print("MySQL error" + e.__str__())
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, param=None):
        """ 执行sql语句 """
        if param == None:
            rowcount = self.cursor.execute(sql)
        else:
            rowcount = self.cursor.execute(sql, param)
        return rowcount

    def select(self, table, cols='*', condition=None):
        if condition is None:
            sql = 'SELECT %s ' % cols + 'FROM %s ' % table
        else:
            sql = 'SELECT %s ' % cols + 'FROM %s ' % table + 'WHERE '+ ' AND '.join(['%s=%r' % (k, condition[k]) for k in condition]) + ';'
        self.cursor.execute(sql)
        fc = self.cursor.fetchall()
        return fc

    def insert(self, table, data):
        ls = [(k, data[k]) for k in data if data[k]]
        sql = 'insert into %s (' % table + ','.join([i[0] for i in ls]) + ') values (' + ','.join(['%r' % i[1] for i in ls]) + ');'
        res = self.cursor.execute(sql)
        self.conn.commit()
        return res

    def update(self, table, dt_update, dt_condition):
        sql = 'UPDATE %s SET ' % table + ','.join(['%s=%r' % (k, dt_update[k]) for k in dt_update]) \
              + ' WHERE ' + ' AND '.join(['%s=%r' % (k, dt_condition[k]) for k in dt_condition]) + ';'
        res = self.cursor.execute(sql)
        self.conn.commit()
        return res

if __name__ == "__main__":
    db = DBManager()
    res = db.select('rank_hsranking', condition={'game_type': 'Standard'})
    print(res)