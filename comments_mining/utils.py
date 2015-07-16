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

# read in file from dist
# input file format: id1 id2 comments
# output: list of string [str1,str2,str3,......]
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

# Chinese word cut
# input format: list of string, which usually is the output from read_comment_from_file()
# output format: 1. list_of_pieces_word: ['word1 word2 word3 word4','word1 word2 word3 word4',.......]
#                2. word_flag: a dict with word as key and [weight, part of speech] as values. For example, {'ÃÀÀö'£º[1,24235, 'n']}
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


# replace punctuation with space
def remove_punctuation(description):
    try:
        result = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+¡ª¡ª£¡£¬¡££¿¡¢~@#£¤%¡­¡­&*£¨£©]+".decode("utf8"), " ".decode("utf8"),description.decode('utf8'))
    except:
        result = ''
    return result


# extract text features by tf-idf and reversed sorted by weight. write into files in the end
# input format: 1. corpus: cutted strings from word_cut function, list_of_pieces_word: ['word1 word2 word3 word4','word1 word2 word3 word4',.......]
#               2. word_category: a dict with word as key and [weight, part of speech] as values. For example, {'ÃÀÀö'£º[1,24235, 'n']}
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


def get_topK(word_weight_category, k = sys.maxint, category_list =['n','v','vd','vn','vf','a','ad','an','ag','al']):
    ff = open('top_k_word_renter_review','w')
    result = []
    i = 0
    for word, weight, category in word_weight_category:
        if category in category_list:
            ff.writelines(word + ' ' + str(weight) + ' ' + category + '\n')
            result.append([word, weight, category ])
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
