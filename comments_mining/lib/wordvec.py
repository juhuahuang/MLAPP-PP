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
# compare_phrase(str1, str2,model): calculate the similarity between two string
# input format:
#                 str1, str2: plain string removed puncuation
#                 model: gensim word vector model, pre-trained
# output format:
#                 similarity: a float represneting two phrase similarity
#                 if_same: a boolean determines if the two strings are similar or not
def compare_phrase(str1, str2,model):
    cut_str1 = []
    cut_str2 = []
    for w in jieba.cut(str1):
        if w in model:
            cut_str1.append(w)
    for w in jieba.cut(str2):
        if w in model:
            cut_str2.append(w)
    if len(cut_str1) == 0 or len(cut_str2) == 0:
        return 0, False
    try:
        similarity = model.n_similarity(cut_str1,cut_str2)
    except:
        print str1,unicode(str2)
        similarity = 0
    return similarity,similarity > 0.6