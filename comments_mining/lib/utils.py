#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'


import sys
import jieba.posseg as pseg
import numpy as np
import jieba
import jieba.analyse
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

reload(sys)
sys.setdefaultencoding('utf8')



def read_in_keys(path):
    ff=open(path)
    keys =set()
    for line in ff:
        tmp = line.split(' ')
        keys.add(tmp[0])
    return keys

# Chinese word cut
# input format: list of string, which usually is the output from read_comment_from_file()
# output format: 1. list_of_pieces_word: ['word1 word2 word3 word4','word1 word2 word3 word4',.......]
#                2. word_flag: a dict with word as key and [weight, part of speech] as values. For example, {'美丽'：[1,24235, 'n']}
def word_cut(list_of_string):
    word_flag={}
    list_of_pieces_word=[]
    for line in list_of_string:
        no_punct_line = remove_punctuation(line)
        try:
            cutted_line = pseg.cut(no_punct_line)
        except:
            continue
        cutted_string =''
        for elem in cutted_line:
            word = elem.word
            flag = elem.flag
            cutted_string = cutted_string + ' ' + word
            word_flag[word] = flag
        list_of_pieces_word.append(cutted_string.strip())
    return list_of_pieces_word, word_flag




# extract text features by tf-idf and reversed sorted by weight. write into files in the end
# input format: 1. corpus: cutted strings from word_cut function, list_of_pieces_word: ['word1 word2 word3 word4','word1 word2 word3 word4',.......]
#               2. word_category: a dict with word as key and [weight, part of speech] as values. For example, {'美丽'：[1,24235, 'n']}
#               3. file_to_write: the file where to write
def tfidf(corpus,word_category,file_to_write):
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    weight = tfidf.toarray()
    sum_weight = np.sum(weight,axis = 0)
    word = vectorizer.get_feature_names()
    word_and_weight=[]
    for i in range(len(sum_weight)):
        word_and_weight.append([word[i],sum_weight[i]])
    word_and_weight.sort(key = lambda key: key[1],reverse = True)
    f = open(file_to_write,'w+')
    result =[]
    for j in range(len(word_and_weight)) :
        try:
            f.write(word_and_weight[j][0]+ ' ' + str(word_and_weight[j][1]) + ' ' +word_category[word_and_weight[j][0]] +"\n")
            result.append([word_and_weight[j][0], word_and_weight[j][1], word_category[word_and_weight[j][0]] ])
        except:
            continue
    f.close()
    return result


def get_topK(word_weight_category, file_to_write,k, category_list):
    ff = open(file_to_write,'w')
    result = []
    i = 0
    for word, weight, category in word_weight_category:
        if category in category_list:
            ff.writelines(word.strip() + ' ' + str(weight) + ' ' + category + '\n')
            result.append([word.strip(), weight, category ])
            i = i+1
        if i > k:
            break
    ff.close()
    return result


def get_car_tag(path,car_id, top_k):
    ff=open(path)
    comments=''
    for line in ff:
        sentence = line.split('\t')
        try:
            if int(sentence[1]) == int(car_id):
                for line in sentence[2:]:
                    comments = comments + line+' '
        except:
            continue
    tags = jieba.analyse.extract_tags(comments, topK= top_k)
    return tags


def remove_punctuation(comment):
    '''
    :param comment:
    :return:
    df['comment'].map(remove_punctuation)
    '''
    try:
        result = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), " ".decode("utf8"),comment.decode('utf8'))
    except:
        result = ''
    return result

def jieba_add_dict(path):
    ff = open(path)
    for word in ff:
        jieba.suggest_freq(word,True)
    ff.close()