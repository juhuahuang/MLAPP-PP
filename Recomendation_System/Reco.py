# -*- coding: utf-8 -*-
import sys
sys.path.append('C:\Users\Administrator\Desktop\MyCode\PyCharm\issues\pdlib\py')

import excel
import jieba
import jieba.analyse
import re

def read_from_file(path):
    result = excel.readExcel(path)[0]
    result= result['data'][1:]
    car_id = [ elem[0] for elem in result]
    car_desc = [elem[1] for elem in result]
    return car_id,car_desc

def word_cut(list_of_string):
    list_of_pieces_word=[]
    for line in list_of_string[:20]:
        no_punct_line = remove_punctuation(line)
        list_of_pieces_word.append(' '.join(jieba.cut(no_punct_line)))
    return list_of_pieces_word

def remove_punctuation(description):
    return re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),description)


car_id,car_desc = read_from_file('C:\Users\Administrator\Desktop\data\car_description\car_description.xlsx')
cutted_car_desc = word_cut(car_desc)
print cutted_car_desc[4]

