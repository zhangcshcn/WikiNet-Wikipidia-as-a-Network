#! /usr/bin/python2
# -*- coding = utf-8 -*-
from __future__ import print_function
import numpy as np
import sys
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import cPickle as pkl


class knowledgeGraph():
    def __init__(self, pagePath):
        ### self.pagePath is the folder where the content containing
        ### a folder of the original html pages, the .stats file, 
        self.pagePath = pagePath
        self.contentPath = 'content'
        self.sim()
        self.buildGraph()
        self.tfidfTitle = TfidfVectorizer(input=u'content', strip_accents='ascii', stop_words='english')
        text_dict = {x:self.idx2url[x][6:].replace('_',' ') for x in self.idx2url}
        self.tfsTitle = self.tfidfTitle.fit_transform(text_dict.values())
        self.mostRelatedPath()

    def sim(self):
        # doing the tfidf and cosine similarity
        flist = os.listdir(self.pagePath + '/' + self.contentPath)
        self.tfidf = TfidfVectorizer(input=u'content', strip_accents='ascii', stop_words='english')
        text_dict = {int(f.strip('.txt')): file('%s/%s/%s' %(self.pagePath, self.contentPath, f)).read() for f in flist}
        fname = text_dict.keys()
        self.row2idx = {i: fname[i] for i in range(len(fname))}
        self.idx2row = {fname[i]: i for i in range(len(fname))}
        self.tfs = self.tfidf.fit_transform(text_dict.values())
        self.cosCoef = (self.tfs * self.tfs.T).toarray()


    def buildGraph(self):
        # building the weighted graph
        self.urlGraph, self.url2idx = pkl.load(file('%s/urlgi.pkl' % (self.pagePath)))
        self.idx2url = {self.url2idx[url]: url for url in self.url2idx}
        self.graph = {}
        mask = np.zeros(self.cosCoef.shape)
        for page in self.urlGraph:
            self.graph[page] = {sub: self.cosCoef[self.idx2row[page], self.idx2row[sub]] for sub in self.urlGraph[page]}
            mask[self.idx2row[page], [self.idx2row[sub] for sub in self.urlGraph[page]]] = 1
        self.cosCoef *= mask
        self.cosCoef[np.eye(len(self.cosCoef)) == 1] = 1
        fp = open('%s_edge.csv' % self.pagePath, 'w')
        for page in self.graph:
            map(fp.write, ['%s %s %f\n' % (self.idx2url[page], self.idx2url[sub], self.graph[page][sub]) for sub in self.graph[page]])
        fp.close()
        # np.save(file('%s/graph.npy' % (self.pagePath), 'w'), self.cosCoef)

    def mostRelatedPath(self):
        self.distance = np.copy(self.cosCoef)
        N = len(self.distance)
        self.route = np.ones(self.distance.shape, dtype=int) * -1
        for i in range(N):
            self.route[i][self.distance[i] != 0] = i
        for k in range(N):
            for i in range(N):
                tmp = self.distance[i, k] * self.distance[k, :]
                isg = self.distance[i, :] < tmp
                self.distance[i, isg] = tmp[isg]
                self.route[i, isg] = k
            if k % 10 == 0:
                print('%6d / %6d \r' % (k, N), end="")
        self.distance[self.distance == 1] = -1
        # np.save(file('%s/dist.npy' % self.pagePath, 'w'), self.distance)
        # np.save(file('%s/path.npy' % self.pagePath, 'w'), self.route)
        return self.distance, self.route

    def matchQuery(self, query):
        titleVec = self.tfidfTitle.transform([query])
        tmp = (self.tfsTitle * titleVec.T).toarray()
        titleID = np.argmax(tmp)
        if tmp[titleID] == 0:
            wordVector = self.tfidf.transform([query])
            docID = np.argmax((self.tfs * wordVector.T).toarray())
            return docID
        else:
            return titleID

    def searchRelated(self, docID):
        descendantID = np.argsort(self.distance[docID, :])[::-1][:20]
        ancestorID = np.argsort(self.distance[:, docID])[::-1][:20]
        #print(self.idx2url[self.row2idx[docID]])
        #print([ self.idx2url[self.row2idx[i]] for i in descendantID])
        #print([ self.idx2url[self.row2idx[i]] for i in ancestorID])
        return descendantID, ancestorID

    def searchRoute(self, doc1, doc2):
        if doc1 == doc2:
            return []
        elif self.route[doc1, doc2] == -1:
            return []
        elif self.route[doc1, doc2] == doc1:
            return [doc1]
        else:
            return self.searchRoute(doc1, self.route[doc1, doc2]) + self.searchRoute(self.route[doc1, doc2], doc2)
    
if __name__ == '__main__':
    G = knowledgeGraph(sys.argv[1])
    with open('%s/class.pkl'%sys.argv[1],'w') as f:
        pkl.dump(G, f)
