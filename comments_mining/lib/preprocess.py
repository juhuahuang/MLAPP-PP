#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'


import sys

sys.path.append('/mnt/work/issues/pdlib/py')
try:
    import mydb
except:
    pass

import re
from pandas import DataFrame

# read in file from disk
def read_comment_from_file(path = '..\data\\test'):
    comments_df = DataFrame.from_csv(path , header=0, sep='\t')
    comments_df.reset_index(inplace=True)
    return comments_df

def get_data_from_db(sql):
    db = mydb.get_db(conv=True)
    comments_data = list(db.exec_sql(sql))
    comments_df = DataFrame(comments_data)
    return comments_df





