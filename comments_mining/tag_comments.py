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
import argparse



class tagging:

    def __init__(self,dict,model_source,tag_source):
        utils.jieba_add_dict(dict)
        self.tag_repo=[]
        self.tags_repo=[]
        for line in open(tag_source):
            self.tags_repo.append(line)
        self.model = gensim.models.Word2Vec.load(model_source)

    def tag_comments_test(self, comments):
        comments = utils.remove_punctuation(comments)
        phrase_tag = set()
        phrase_list = comments.split(' ')
        for p in phrase_list:
            for t in self.tags_repo:
                match_part, if_same = wordvec.compare_phrase(p, t,self.model)
                if if_same:
                    phrase_tag.add((p,t))
        return phrase_tag

    def tag_comments_database(self, comments):
        comments = utils.remove_punctuation(comments)
        phrase_tag = set()
        phrase_list = comments.split(' ')
        for p in phrase_list:
            for t in self.tags_repo:
                match_part, if_same = wordvec.compare_phrase(p, t,self.model)
                if if_same:
                    phrase_tag.add(t)
        return phrase_tag

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


    # dict = args.dict
    # wordvec_source = args.wordvec
    # tag = args.tag
    # id = args.carID
    # sql = '''select `comment` from order_reviews where carID = %s''' % id
    # pydb = mydb.get_db()
    # comments = pydb.exec_sql(sql)
    # comments = [c['comment'] for c in comments]
    # make_tag = tagging(dict,wordvec_source,tag)


    # make_tag = tagging('test_dict','data/wordvec_model','artificial_tag')
    # comments = [
    #     '驾驶轻松动力足，gps等配备齐全，空间巨大，坐五个人一点都不挤。后备箱也超大，只有塞不满没有装不下。',
    #     '车况好 商务车 车主特别好',
    #     '车主人好，车也很好用。车辆省油，整洁干净，车主和气，很好',
    #     '车很好开，车主人也很好说话～',
    #     '感觉这车开的挺舒服的，车主和PP网都挺好的，下次还选PP，加油！'
    # ]
    # result = map(make_tag.tag_comments,comments)
    utils.print2file('test',result)