#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2015 Juhua Huang.
# Author: Juhua Huang <hjh.1222@gmail.com>
# Version: : 
# FileName: 
# Date: <2015>
# Description: 


import sys
sys.path.append('lib')
import mydb
import numpy as np
import utils
import preprocess
import gensim
import wordvec
import jieba
import argparse





def tag_comments(comments,dict,model_source,tag_source):
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
    ff = open('test','w')
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
    parser = argparse.ArgumentParser(description='train word vector')
    parser.add_argument('-i', '--carID',type=str,help ='car ID')
    parser.add_argument('-s', '--tag', default= 'data/all_comments',type=str,help ='tag file path')
    parser.add_argument('-u', '--dict', default= 'data/udf_dict',type=str,help ='UDF dict path')
    parser.add_argument('-o', '--wordvec', default= 'data/wordvec_model',type=str,help ='output file name')
    args = parser.parse_args()


    source = args.source
    dict = args.dict
    wordvec = args.wordvec
    tag = args.tag
    id = args.carID
    sql = '''select `comment` from order_reviews where carID = %s''' % id
    pydb = mydb.get_db()
    comments = pydb.exec_sql(sql)
    comments = [c['comment'] for c in comments]
    # comments = ['第一次租车还比较紧张，但是车主非常好，借车的时候联系了下还帮我开到方便的地方交车，而且车保养的非常好，很干净很好开，车主人也非常好沟通，实在是太赞了',
    #         '车子坐起来蛮舒服的 就是一档换二档有点困难 总体车主人也很好 很容易沟通',
    #         '车空间大，省油，车况好！第一次PP网上租车，非常方便 ，离家比较近，取还车很省时。车主是个阳光大男孩，很帅很好沟通。还会再来租~']
    tag_comments(comments,dict,wordvec,tag)