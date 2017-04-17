# /usr/bin/python2
# -*- coding = utf-8 -*-
import sys
import os
from bs4 import BeautifulSoup as bs
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import string
import cPickle as pkl
from nltk import word_tokenize


if __name__ == '__main__':
    pagePath = 'apple_inc'
    contentPath = 'content'
    flist = os.listdir(pagePath + '/' + contentPath)

    tfidf = TfidfVectorizer(
        input=u'content', strip_accents='ascii', stop_words='english')
    
    text_dict = {int(f.strip('.txt')): file('%s/%s/%s'%(pagePath,contentPath,f)).read() for f in flist}
    fname = text_dict.keys()
    row2idx = {i: fname[i] for i in range(len(fname))}
    idx2row = {fname[i]: i for i in range(len(fname))}
    tfs = tfidf.fit_transform(text_dict.values())
    cosCoef = (tfs * tfs.T).toarray()
    #print [x for x in tfidf.get_feature_names()]
    pkl.dump((tfs, cosCoef, row2idx, idx2row, tfidf), file(pagePath + '_tfidf.pkl', 'w'))
