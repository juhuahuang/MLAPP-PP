#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
sys.path.append('./lib')
import jieba
import numpy as np
import utils
import preprocess
import gensim
import wordvec
import argparse
from pandas import DataFrame
__author__ = 'Administrator'



def train_word_vector(source,dict,wordvec):
    utils.jieba_add_dict(dict)
    comments_df = DataFrame.from_csv(source,sep = '\t')
    document = []
    for line in comments_df['comment'].values:
        line =  utils.remove_punctuation(line)
        cutted_line = jieba.cut(line)
        document.append(list(cutted_line))
    model = gensim.models.Word2Vec(document)
    print 'saving word vector model'
    model.save(wordvec)
    return model

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    parser = argparse.ArgumentParser(description='train word vector')
    parser.add_argument('-s', '--source', default= 'data/all_text',type=str,help ='file path')
    parser.add_argument('-u', '--dict', default= 'data/udf_dict',type=str,help ='UDF dict path')
    parser.add_argument('-o', '--wordvec', default= 'data/wordvec_model',type=str,help ='output file name')
    args = parser.parse_args()

    source = args.source
    dict = args.dict
    wordvec = args.wordvec

    train_word_vector(source,dict,wordvec)

