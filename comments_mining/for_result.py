#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Administrator'
import sys
import numpy as np
sys.path.append('./lib')

import utils
import preprocess
import match_comments as mc
import string


comments_df = preprocess.read_comment_from_file('data/order_review')
comments = comments_df['comment'].iloc[:]
keys = utils.read_in_keys("top_k_'test'")
result = comments.apply(mc.tag_comments,args = (keys,))
result.to_csv('comment_with_tag', sep='\t', encoding='utf-8')
bag_of_tags = set()
for line in result:
	tmp = line.split('>>')[-1]
	tags = tmp.split('\t')
	tags = map(string.strip,tags)
	bag_of_tags = bag_of_tags.union(set(tags))
ff = open('tags','w')
for t in bag_of_tags:
	ff.write(t +'\n')
ff.close()
