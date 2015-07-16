# -*- coding: utf-8 -*-
import sys

#import excel
import jieba.posseg as pseg
import numpy as np
import jieba
import jieba.analyse
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

reload(sys)
sys.setdefaultencoding('utf8')

def read_comment_from_file(path):
	ff=open(path)
	comments=[]
	for line in ff:
		sentence = line.split('\t')
		comments.extend(sentence[2:])
	return comments


def read_in_dict(path):
    ff=open(path)
    word_dict ={}
    for line in ff:
        space_index = line.index(' ')
        word = line[:space_index]
        count = int(line[space_index:])
        word_dict[word] = count
    return word_dict


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
	for word, flag in cutted_line:
		cutted_string = cutted_string + ' ' + word
		word_flag[word] = flag 
        list_of_pieces_word.append(cutted_string.strip())
    return list_of_pieces_word, word_flag

def remove_punctuation(description):
    try:
        result = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), " ".decode("utf8"),description.decode('utf8'))
    except:
        result = ''
    return result

def tfidf(corpus,word_category):
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    weight = tfidf.toarray()
    sum_weight = np.sum(weight,axis = 0)
    word = vectorizer.get_feature_names()
    word_and_weight=[]
    for i in range(len(sum_weight)):
        word_and_weight.append([word[i],sum_weight[i]])
	word_and_weight.sort(key = lambda key: key[1], reverse = True)
    f = open('tfidf_word_renter_review','w+')
    for j in range(len(word_and_weight)) :
        try:
            f.write(word_and_weight[j][0]+ ' ' + str(word_and_weight[j][1]) + ' ' +word_category[word_and_weight[j][0]] +"\n")
        except:
			continue
    f.close()


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


comment = read_comment_from_file('renter_review')
cutted, word_category = word_cut(comment)
tfidf(cutted, word_category)

#jieba.analyse.set_idf_path("tfidf_word");

#tags = get_car_tag('hackthon',5078,20)
#print(",".join(tags))



