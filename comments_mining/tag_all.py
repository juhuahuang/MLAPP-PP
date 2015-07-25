#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2015 Juhua Huang.
# Author: Juhua Huang <hjh.1222@gmail.com>
# Version: : 
# FileName: 
# Date: <2015>
# Description: 



import sys
sys.path.append('./lib')
# import mydb
import numpy as np
import utils
import preprocess
import gensim
import wordvec
import jieba
import tag_comments
from pandas import DataFrame

if __name__=="__main__":
    # sql = 'select carID, `comment` from renter_reviews where LENGTH(`comment`) > 24'
    # db = mydb.get_db(conv=True)
    # comments_data = list(db.exec_sql(sql))
    # comments_df = DataFrame(comments_data)
    result = DataFrame()
    comments_df = DataFrame.from_csv('data/comments',sep = '\t')
    comments_df = comments_df[:100]
    comments_df[['carID']] = comments_df[['carID']].astype(int)
    print 1
    make_tag = tag_comments.tagging('data/udf_dict','data/wordvec_model','data/artificial_tag')
    print 2
    # comments_df['tags'] = comments_df[:30]['comment'].map(make_tag.tag_comments)
    comments_df['tags'] = comments_df['comment'].map(make_tag.tag_comments)
    print 3
    comments_df['tags'] = comments_df['tags'].map(utils.print_listoflist2string)
    comments_df.to_csv('tag_all',sep='#')