from django.shortcuts import render
from django.template import loader
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils import timezone
import sys, os
import cPickle as pkl
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import knowledgeGraph

sys.modules['knowledgeGraph']=knowledgeGraph
with open('wikiNet/class_dev.pkl') as f:
    G = pkl.load(f)

def index(request):
    return render(request, 'index.html')

def search(request):
    global G
    query = request.GET.get('query', None)
    docID = G.matchQuery(query)
    dID,aID = G.searchRelated(docID)
    queryAnchor = (G.idx2url[G.row2idx[docID]], G.idx2url[G.row2idx[docID]][6:].replace("_", " "))
    dList = zip([G.idx2url[G.row2idx[i]] for i in dID], [G.idx2url[G.row2idx[i]][6:].replace("_", " ") for i in dID])
    aList = zip([G.idx2url[G.row2idx[i]] for i in aID], [G.idx2url[G.row2idx[i]][6:].replace("_", " ") for i in aID])
    return render(request, 'matchResult.html',{'queryTitle': queryAnchor, 'dList': dList, 'aList': aList})
    

def route(request):
    global G
    src = request.GET.get('src', None)
    dst = request.GET.get('dst', None)
    srcID = G.matchQuery(src)
    # print srcID
    dstID = G.matchQuery(dst)
    # print dstID
    route = G.searchRoute(srcID, dstID)
    srcAnchor = (G.idx2url[G.row2idx[srcID]], G.idx2url[G.row2idx[srcID]][6:].replace("_", " "))
    dstAnchor = (G.idx2url[G.row2idx[dstID]], G.idx2url[G.row2idx[dstID]][6:].replace("_", " "))
    if route != []:
        route.append(dstID)
        routeList = zip([G.idx2url[G.row2idx[i]] for i in route], [G.idx2url[G.row2idx[i]][6:].replace("_", " ") for i in route])
    else:
        routeList = []
    return render(request,'routeResult.html',{'isRoute': len(route), 'srcTitle': srcAnchor, 'dstTitle': dstAnchor, 'routeList': routeList})
    