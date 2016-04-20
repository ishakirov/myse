from django.shortcuts import render
from django.http import HttpResponse

from SearchEngine import SearchEngine

import redis
import json

def index(request):
    se = SearchEngine()
    query = request.GET.get('q', '')
    result = []
    if len(query) > 1:
        result = se.boolSearch(query)

    return render(request, 'search/index.html', {'query': query, 'result': result, 'len': len(result)})

def meta(request):
    se = SearchEngine()
    query = request.GET.get('q', '')
    result = []
    if len(query) > 1:
        result = se.metaSearch(query)
    return render(request, 'search/meta.html', {'query': query, 'result': result, 'len': len(result)})

def metaAuthors(request):
    se = SearchEngine()
    query = request.GET.get('q', '')
    return HttpResponse(json.dumps(se.getAuthors(query)), content_type="application/json")

def keywords(request):
    se = SearchEngine()
    query = request.GET.get('q', '')
    result = []
    if len(query) > 1:
        result = se.tfidfSearch(query)
    return render(request, 'search/keywords.html', {'query': query, 'result': result, 'len': len(result)})
