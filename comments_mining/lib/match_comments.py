#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'


import sys
import string
import utils
reload(sys)
sys.setdefaultencoding('utf8')
from pandas import DataFrame

def read_keyword_from_file(path = '..\data\\test'):
    keyword_df = DataFrame.from_csv(path, header=-1, sep=' ')
    keyword_df.reset_index(inplace=True)
    return keyword_df

def read_all_comments_from_file(path = '..\data\\all_comments'):
    all_comments_df = DataFrame.from_csv(path, header=0, sep='\t')
    all_comments_df.reset_index(inplace=True)
    return all_comments_df


def search_keywords(comments,keywords):
    result = set()
    for key in keywords:
        if comments.find(key) >-1:
            result.add(key)
    return result


def keys_recall_comments(comment_set,keywords):
    car_keywords={}
    for ind in comment_set:
        car_id = comment_set['carID'].iloc[ind]
    	comments = string.strip(str(comment_set['comment'].iloc[ind]))
    	if car_id not in car_keywords.keys():
            car_keywords[car_id] =set()
    	key_sets = search_keywords(comments,keywords)
    	car_keywords[car_id] = car_keywords[car_id].union(key_sets)

def tag_comments(comment,keys):
    tags = set()
    comment = utils.remove_punctuation(comment)
    comment = comment.strip(' ')
    split_comment = comment.split(' ')
    ff = open('../data/tag_comments','w')
    for phrase in split_comment:
        phrase = phrase.strip(' ')
        for key in keys:
            if phrase.find(key) > -1:
                if len(phrase) < 7 and len(phrase) >2:
                    #len(phrase) 返回的是中文字的个数，不是真实长度（中文字×3）
                    comment = comment.replace(phrase,"$%s$" % (phrase))
                    tags.add(phrase)
        result =  "%s >> %s" % (comment.rstrip(), "\t".join(list(tags)))
    return result


#
# df=read_keyword_from_file(path = '..\data\\top_k_word_order_review')
# all_comments = read_all_comments_from_file( '..\data\\all_comments')
# keywords=df[0]
#
# car_keywords = {}
# for ind in all_comments.index:
#     car_id = all_comments['carID'].iloc[ind]
#     comments = string.strip(str(all_comments['comment'].iloc[ind]))
#     if car_id not in car_keywords.keys():
#         car_keywords[car_id] =set()
#     key_sets = search_keywords(comments,keywords)
#     car_keywords[car_id] = car_keywords[car_id].union(key_sets)
#
# result =[]
# for id in car_keywords:
#     counts = len(car_keywords[id])
#     result.append([id,counts])
# result.sort(key = lambda key: key[1],reverse = True)
# print result
# ff = open('tags_count','w')
# for line in result:
#     ff.writelines(str(line[0]) + ' ' + str(line[1]) + '\n')
# ff.close()

# tag_comments('what a nice day',['what', 'nice'])
#


