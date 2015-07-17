#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import argparse
import numpy as np
sys.path.append('./lib')
sys.path.append('/mnt/work/issues/pdlib/py')
import utils
import preprocess

def main():
    parser = argparse.ArgumentParser(description='take text feature')
    parser.add_argument('-t', '--type', type=str, choices=('db', 'file'), default='file', help='db/file')
    parser.add_argument('-s', '--source', type=str,help ='file path/sql script')
    parser.add_argument('-n', '--name', type=str,help ='output file name')
    parser.add_argument('-k', '--topk', type=int,default= 500, help ='top k words')
    parser.add_argument('-w', '--word_category', default='a,ad,an,ag,al', type=str,help ='word category')
    args = parser.parse_args()

    source_from = args.type
    source = args.source
    name = args.name
    k_num = args.topk
    word_category = args.word_category.split(',')
    if source_from == 'db':
        comments_df = preprocess.get_data_from_db(source)
    elif source_from == 'file':
        comments_df = preprocess.read_comment_from_file(source)
    else:
        return

    comments_list = list(comments_df['comment'].values)
    cutted, word_category = utils.word_cut(comments_list)
    word_weight_flag = utils.tfidf(cutted, word_category,'tfidf_' + name)
    key_word = utils.get_topK(word_weight_flag,'top_k_' +name, k = k_num, category_list =word_category)


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    main()