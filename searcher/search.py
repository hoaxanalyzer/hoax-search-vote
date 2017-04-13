#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provide search interface for selected search engines"""

import requests
from lxml import html
import urllib.parse

__author__ = "Feryandi Nurdiantoro"

exclusion = ["facebook.com",\
             "youtube.com",\
             "twitter.com",\
             "blogspot.com",\
             "pinterest.com",\
             "amazon.com",\
             "wordpress.com",\
             "smule.com",\
             "tumblr.com",\
             "instagram.com",\
             "scribd.com"]

def search(obj):
  """ Generic function for searching different search engine, return url and title of results 

  obj contains:
  keyword: the search keyword
  url: base url of the search engine
  payload: get parameter needed
  htmlclass: the class where the result is contained
  urlkey: used when the url retrieved need to be sanitized
  max_results: number of maximum results retrieved
  """
  keyword = obj["keyword"]
  url = obj["url"]
  payload = obj["payload"]
  htmlclass = obj["htmlclass"]
  urlkey = obj["urlkey"]
  max_results = obj["max_results"]

  data = []
  r = requests.get(url, params=payload)
  doc = html.fromstring(r.text)

  result = 0
  for a in doc.cssselect(htmlclass):
    site = {}
    site["url"] = sanitize_url(a.get('href'), urlkey)
    o = urllib.parse.urlparse(site["url"])
    site["url"] = o.scheme + "://" + o.netloc + o.path
    if check_url(site["url"]): 
      site["title"] = a.text_content()
      data.append(site)
      result += 1
    if max_results and max_results < result:
      return data 
  return data

def sanitize_url(url, key=None):
  """ Return sanitized url when needed (when the key is not None) """
  if key is not None:
    parsed_url = urllib.parse.urlparse(url)
    redirect_url = urllib.parse.parse_qs(parsed_url.query)[key]
    return redirect_url[0]
  return url

def check_url(url):
  """ Simply check if the retrieved URL is in exclusion list """
  for blacklist in exclusion:
    if blacklist in url.lower():
      return False
  return True

def bing(keyword):
  """ Interface for Bing search """
  exc = ' -' + ' -'.join(exclusion)
  data = {}
  data["keyword"] = keyword + exc
  data["url"] = "https://www.bing.com/search"
  data["payload"] = {
    'q': keyword,
    'qs': 'n',
    'form': 'QBLH',
    'sp': '-1',
    'pq': keyword,
    'sc': '0-0',
  }
  data["htmlclass"] = '.b_algo h2 a'
  data["urlkey"] = None
  data["max_results"] = 10
  return data

def duckduckgo(keyword):
  """ Interface for Duckduckgo search """
  data = {}
  data["keyword"] = keyword
  data["url"] = "https://duckduckgo.com/html/"
  data["payload"] = {
    'q': keyword,
    's': '0',
  }
  data["htmlclass"] = '#links .links_main a.result__a'
  data["urlkey"] = 'uddg'
  data["max_results"] = 20
  return data

if __name__== "__main__":
  import time
  start = time.time()
  print(search(bing("habibie meninggal")))
  print(search(duckduckgo("habibie meninggal")))
  end = time.time()
  print("Elapsed: " + str(end-start))
