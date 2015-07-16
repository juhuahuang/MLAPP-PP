# -*- coding: utf-8 -*-

__author__ = 'Administrator'


import sys

sys.path.append('/mnt/work/issues/pdlib/py')

#import mydb
import re


def get_data( min_review_num):
    db = mydb.get_db(conv=True)

    sql_script = '''
                     select r.carID, r.`comment` from order_reviews r join
                      (select carID,count(carID) n from order_reviews  GROUP BY carID) tmp on
                      r.carID = tmp.carID and tmp.n> %s

                    ''' % (str(min_review_num))
    comments_data = list(db.exec_sql(sql_script))

    data_cleansing(comments_data)


def data_cleansing(data):
    map(remove_punctuation,data)
    filter(check_chinese, data)


def remove_punctuation(elem):
    try:
        elem['comment'] = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),elem['comment'].decode("utf8"))
    except:
        elem = None
    return elem

def check_chinese(elem):
    check_str = elem['comment']
    for ch in check_str.decode('utf-8'):
        if ch < u'\u4e00' or ch > u'\u9fff':
            return False
    return True

#get_data(50)

xx = [{'id':12,'comment':'中文测试'},{'id':14,'comment':'vely vely gleat'}]
print xx
filter(check_chinese,xx)
print xx
