#!/usr/bin/env python
#-*-coding:utf-8 -*-

#########################################################################
# File Name: tag.py
# Author: garyci
# mail: ciyuanlong@ppzuche.com
# Created Time:Sat Jul 11 01:18:05 2015
#########################################################################
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

synonymWord_d = {}
for line in open(sys.argv[1]):
    lines = line.rstrip().split()
    for i in range(1, len(lines)):
        synonymWord_d[ lines[i] ] = lines[0]


for line in open(sys.argv[2]):
    tags = set() 
    for key in synonymWord_d.keys():
        if line.find(key) > -1:
            line = line.replace(key,"#$!%s!$#" % (key))
            tags.add(synonymWord_d[key])
    print "%s\t%s" % (line.rstrip(), "\t".join(list(tags)))
