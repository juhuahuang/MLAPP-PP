#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import jieba
import numpy as np
sys.path.append('./lib')
import utils
import preprocess
import gensim
__author__ = 'Administrator'


def calculate_word_vector_model(input_path,output_path = None):
    document = []
    for line in open(input_path):
        line =  utils.remove_punctuation(line)
        cutted_line = jieba.cut(line)
        document.append(list(cutted_line))
    model = gensim.models.Word2Vec(document)
    model.save(output_path)
    return model

def compare_phrase(str1, str2,model):
    if len(str1) < 6 or len(str2) < 6:
        return 0, False
    cut_str1 = list(jieba.cut(str1))
    cut_str2 = list(jieba.cut(str2))
    try:
        similarity = model.n_similarity(cut_str1,cut_str2)
    except:
        print str1,unicode(str2)
        similarity = 0
    return similarity,similarity > 0.6