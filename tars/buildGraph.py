#! /usr/bin/python2
# -*- coding = utf-8 -*-
import numpy as np
import sys, os
import cPickle as pkl 


pagePath = 'apple_inc'
contentPath = 'content'
tfs, cosCoef, row2idx, idx2row, tfidf = pkl.load(file(pagePath + '_tfidf.pkl'))
urlGraph, url2idx = pkl.load(file('%s/urlgi.pkl'%(pagePath)))
idx2url = { url2idx[url]: url for url in url2idx }
graph = {}
for page in urlGraph:
    graph[page] = {sub:cosCoef[idx2row[page],idx2row[sub]] for sub in urlGraph[page]}
print 'dumping'
fp = open('%s_edge.csv'%pagePath,'w')
for page in graph:
    map(fp.write,['%s %s %f\n'%(idx2url[page],idx2url[sub],graph[page][sub]) for sub in graph[page]])
fp.close()
pkl.dump(graph,file('%s/graph.pkl'%(pagePath),'w'))