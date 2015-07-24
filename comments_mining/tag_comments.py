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
import mydb
import numpy as np
import utils
import preprocess
import gensim
import wordvec
import jieba
import argparse





def tag_comments(comments,dict,model_source,tag_source,file_to_write):
    utils.jieba_add_dict(dict)
    tags_repo=[]
    for line in open(tag_source):
        tags_repo.append(line)
    model = gensim.models.Word2Vec.load(model_source)
    comments = map(utils.remove_punctuation,comments)
    phrase_tag = set()
    for c in comments:
        phrase_list = c.split(' ')
        for p in phrase_list:
            for t in tags_repo:
                match_part, if_same = wordvec.compare_phrase(p, t,model)
                if if_same:
                    phrase_tag.add((p,t))
    ff = open(file_to_write,'w')
    for s in phrase_tag:
        towrite = ''
        for e in s:
            towrite = towrite + '\t'+ e
        ff.write(towrite+'\n')
    ff.close()
    return towrite


if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    parser = argparse.ArgumentParser(description='tag comments')
    parser.add_argument('-i', '--carID',type=str,help ='car ID')
    parser.add_argument('-t', '--tag', default= 'data/tags',type=str,help ='tag file path')
    parser.add_argument('-u', '--dict', default= 'data/udf_dict',type=str,help ='UDF dict path')
    parser.add_argument('-w', '--wordvec', default= 'data/wordvec_model',type=str,help ='word vector model')
    parser.add_argument('-o', '--output', default= 'data/test',type=str,help ='output file name')
    args = parser.parse_args()


    dict = args.dict
    wordvec_source = args.wordvec
    tag = args.tag
    id = args.carID
    output = args.output
    sql = '''select `comment` from order_reviews where carID = %s''' % id
    pydb = mydb.get_db()
    comments = pydb.exec_sql(sql)
    comments = [c['comment'] for c in comments]

    tag_comments(comments,dict,wordvec_source,tag,output)