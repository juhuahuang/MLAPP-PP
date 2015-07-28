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
    cut_str1 = list(jieba.cut(str1))
    cut_str2 = list(jieba.cut(str2))
    result = []
    for ss in cut_str1:
        if ss not in model:
            continue
        # upper_ss_threshold = model[ss].mean() + 2*model[ss].std()
        # lower_ss_threshold = model[ss].mean() - 2*model[ss].std()
        upper_ss_threshold = 0.6
        lower_ss_threshold = -0.5
        for tt in cut_str2:
            if tt not in model:
                continue
            # upper_tt_threshold = model[tt].mean() + 2*model[tt].std()
            # lower_tt_threshold = model[tt].mean() - 2*model[tt].std()
            upper_tt_threshold = 0.6
            lower_tt_threshold = -0.5
            similarity = model.similarity(ss,tt)
            if similarity < min(lower_ss_threshold, lower_tt_threshold):
                return [],False
            if similarity > max(upper_ss_threshold, upper_tt_threshold):
                result.append([ss,tt,similarity])
                break
    if len(cut_str2) ==1 or len(cut_str1) == 1:
        return result, len(result) >= 1
    return result,len(result) >=2