#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import jieba
import numpy as np
sys.path.append('./lib')
sys.path.append('/mnt/work/issues/pdlib/py')
import utils
import preprocess
import gensim
import wordvec
__author__ = 'Administrator'


#
# for line in open('data/tags'):
#     jieba.suggest_freq(line.strip(),True)
#
# document = []
# for line in open('data/all_comments'):
#     line =  utils.remove_punctuation(line)
#     cutted_line = jieba.cut(line)
#     document.append(list(cutted_line))
# model = gensim.models.Word2Vec(document)
# model.save('wordvec_model_tag')

model = gensim.models.Word2Vec.load('data/wordvec_model')
print model.similarity(u'差',u'好')


tags =[]
tag_mapping = {}
for line in open('data/tags'):
    tags.append(line.strip('\n'))
for tag_iter1 in tags:
    if tag_iter1 in tag_mapping.keys():
        continue
    else:
        tag_mapping[tag_iter1] = tag_iter1
    for tag_iter2 in tags[1:]:
        v,same_meaning= wordvec.compare_phrase(tag_iter1.strip(),tag_iter2.strip(),model)
        if same_meaning:
             tag_mapping[tag_iter2] = tag_iter1
ff = open('synonyms','w')
for key in tag_mapping:
    ff.write('%s\t%s\n' % (key, tag_mapping[key]))
    print key, tag_mapping[key]
ff.close()
