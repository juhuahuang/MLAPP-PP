#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'


import sys
import numpy as np
import jieba
import jieba.analyse


from pandas import DataFrame


class car_cluster :

	def __init__(self,path):
		car_info = DataFrame.from_csv(path,header=0, sep='\t')
		car_info['engine_cap'] =car_info['engine_cap'].apply(self.engine_map)
				
	def engine_map(self,capacity):
		if capacity.rstrip() == 'Below 1,600cc':
			return 0
		elif capacity.rstrip() == '1,600cc to 2,000cc':
			return 1
		elif capacity.rstrip() == '2,001cc to 2,400cc':
			return 2
		elif capacity.rstrip() == 'Above 2,400cc':
			return 3
		else:
			return -1

ff = car_cluster('../data/car_feature')

