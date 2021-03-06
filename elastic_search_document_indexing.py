# -*- coding: utf-8 -*-
"""Elastic Search - Document Indexing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1t4cqYuGdLZfZrtdo-vWuBdUhjnYQKJtM

# Document Indexing

Using python and Elastic Search.

# Install and import packages
"""

pip install elasticsearch

pip install PyPDF2

from elasticsearch import Elasticsearch
import os
import glob
import PyPDF2
import pandas as pd

"""# Locate PDFs"""

os.chdir("/content/temp pdfs")
files = glob.glob("*.*")

# number of files in folder
len(files)

for book in files:
  print(book)

"""# Extract texts from PDFs"""

# create a dataframe with extracted texts

def extractPDFfiles(files):

  this_loc = 1
  df = pd.DataFrame(columns = ("name", "content")) # create empty dataframe

  for file in files: # for each file/document in folder
    pdfFileObj = open(file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    n_pages = pdfReader.numPages
    this_doc = '' # create empty document object

    for i in range(n_pages): # for each page in file/document
      pageObj = pdfReader.getPage(i)
      this_text = pageObj.extractText()
      this_doc += this_text # concatenate texts from each page
    
    df.loc[this_loc] = file, this_doc # put extracted information in the dataframe
    this_loc = this_loc + 1 # go to the next row on the dataframe
  
  return df

df = extractPDFfiles(files)

df.head()

df.iloc[3,1]

df.shape[0], df.shape[1] # files, columns

"""# Indexing documents"""

!wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.0.0-linux-x86_64.tar.gz -q
!tar -xzf elasticsearch-7.0.0-linux-x86_64.tar.gz
!chown -R daemon:daemon elasticsearch-7.0.0
# start server
import os
from subprocess import Popen, PIPE, STDOUT
es_server = Popen(['elasticsearch-7.0.0/bin/elasticsearch'], 
                  stdout=PIPE, stderr=STDOUT,
                  preexec_fn=lambda: os.setuid(1)  # as daemon
                 )

# wait a bit then test
!curl -X GET "localhost:9200/"

# instantiate
es = Elasticsearch()

# test connection to the elastic search cluster
es.ping()

"""## Create Index"""

# create index
es.indices.create(index='ex', ignore=[400, 404])

df.columns

col_names = df.columns
for row_number in range(df.shape[0]): # for all rows in the dataframe
  body = dict([(x, str(df.iloc[row_number][x])) for x in col_names]) # create dictionary for each field
  es.index(index = 'ex', body = body) # indexing body on the index 'ex'

body

"""# Search"""

search_results = es.search(index = 'ex',
                           body = {"_source" : "name", # return name column
                                   "query" : {
                                       'match_phrase' : {"content" : "sombra"}, # word/phrase to search for
                                             }
                                   })

search_results['hits']['total']

search_results['hits']['total']['value']

search_results['hits']

search_results

res = es.search(index = 'ex',
                body = {"_source" : "name", # return name column
                        "query" : {
                            'match_phrase' : {"content" : "vinho"}, # word/phrase to search for
                                  }
                        })

print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
    print(hit["_source"]['name']) # print only the name

res = es.search(index="ex", body={"query": {
                                       'match_phrase' : {"content" : "ghost"}, # word/phrase to search for
                                            }
                                 })

print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
    print(hit["_source"]['name']) # print only the name