import math
import time

import numpy as np
from scipy import spatial

from ranker import Ranker
import utils
from gensim.models import KeyedVectors

# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model
        self.index_word_set = self._model.wv.index2word
        self.vector_dictionary = {}

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        query_as_list = self._parser.parse_query(query) ### line 41  override the existing array without adding the query words
        query_as_list1 = self.create_syno_arr(query_as_list)
        query_arr=[]
        for key in query_as_list.keys():
            if key not in query_arr:
                query_arr.append(key)
        for i in query_as_list1:
            if i not in query_arr:
                query_arr.append(i)

        relevant_docs = self._relevant_docs_from_posting(query_arr)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        queryVec = self.average_vector(query_as_list)
        for key in query_as_list:
            if key in self._indexer.inverted_idx.keys():
                arr = self._indexer.inverted_idx[key][1]
                for tup in arr:
                    if tup[1] not in relevant_docs.keys():
                        tweet_id = tup[1]

                        dictVec = self._indexer.inverted_idx[tweet_id][3]
                        dist = 1-spatial.distance.cosine(dictVec,queryVec)
                        relevant_docs[tweet_id] = dist

        return relevant_docs

    def average_vector(self, dictionary):
        vector = np.zeros((300,))  ##init matrix [0,0,0,0......0 ->300 time]
        words = [word for word in dictionary if word in self.index_word_set]
        if len(words) >= 1:
            return np.mean(self._model[words], axis=0)
        else:
            return np.zeros((300,))

        # for word in dictionary:
        #     counter=0
        #     if word in self.index_word_set:
        #         counter+=1
        #         vector = np.add(vector,self._model[word])
        #     ##why not devide by number of words?

        return vector

    def create_syno_arr(self,dict):
        arr = []
        for key in dict.keys():
            try:
                syno_arr = self._model.most_similar(key,topn=4)
                for syno in syno_arr:
                    if '@' in syno[0]:
                        continue
                    else:
                        arr.append(syno[0])
            except:
                arr.append(key)
        return arr

    def Word2VecSim(self,query,doc):

        #print(doc)
        zero_vector = np.zeros((300,))
        query_vector = self.average_vector(query)
        # print(f"query vector      :{query_vector}")
        if np.array_equal(zero_vector, doc):
            return 0
        else:
            try:
                return 1 - spatial.distance.cosine(doc, query_vector)
            except RuntimeWarning:
                print(doc)
                print("///////")
                print(query_vector)
                exit()


    def CossimVectors(self,query,doc):
        return self.numer(query,doc)/self.denumer(query,doc)

    def numer(self, query, doc):
        num = 0
        for term in query.keys():
            if term in doc.keys():
                num += query[term]*doc[term]
        return num


    def denumer(self, query , doc):
        denum = 0
        for term in doc.keys():
            denum += doc[term]*doc[term]
        try:
            denum = math.sqrt(denum)*math.sqrt(len(query))
        except:
            print(doc)
            print("///////")
            print(query)
            exit()
        return denum
