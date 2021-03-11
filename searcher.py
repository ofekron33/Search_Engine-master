
import time
from spellchecker import SpellChecker

import numpy as np
from scipy import spatial
from ranker import Ranker

from nltk.corpus import wordnet as wn
from nltk.corpus import lin_thesaurus as t






class Searcher:
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self.spellcheck=SpellChecker()
        self.spell_arr=['MI6','lmfao','bbc','5G','IMO','ffs','tv','9th','wuhan','covid','rt','Co2','dr','fauci','CDC','cdc','co2','c02','Dr','faucis','PM','pm','ppp']

        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model
        self.index_word_set = self._model.wv.index2word
        self.vector_dictionary = {}

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
                arr = self._indexer.inverted_idx[key][0]
                for tup in arr:
                    if tup not in relevant_docs.keys():
                        tweet_id = tup
                        #dictVec = 0
                        if self._indexer.postingDict[tweet_id][2] == 0:
                            dictVec = self.average_vector(self._indexer.postingDict[tweet_id][0])

                        else:
                            dictVec = self._indexer.postingDict[tweet_id][1]

                        # dictVec = self._indexer.postingDict[tweet_id][1]

                        dist = 1 - spatial.distance.cosine(dictVec, queryVec)

                        relevant_docs[tweet_id] = dist

        return relevant_docs


    def average_vector(self, dictionary):
        vector = np.zeros((300,))  ##init matrix [0,0,0,0......0 ->300 time]
        words = [word for word in dictionary if word in self.index_word_set]
        if len(words) >= 1:
            return np.mean(self._model[words], axis=0)
        else:
            return np.zeros((300,))
        return vector

    def create_syno_arr(self,dict):
        arr = []
        for key in dict.keys():
            try:
                syno_arr = self._model.most_similar(key,topn=6)
                for syno in syno_arr:
                    if '@' in syno[0]:
                        continue
                    else:
                        arr.append(syno[0])
            except:
                arr.append(key)
        return arr



    def search2(self, query, k=None): ###WORDNET ONLY
        query_as_list = self._parser.parse_query(query)  ### line 41  override the existing array without adding the query words
        query_as_list1 = self.word_net_synonyms(query_as_list)
        query_arr = []
        if (len(query_as_list1) > 0):
            for i in query_as_list1:
                if i not in query_arr:
                    query_arr.append(i)
        for key in query_as_list.keys():
            if key not in query_arr:
                query_arr.append(key)
        relevant_docs = self._relevant_docs_from_posting(query_arr)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, ranked_doc_ids












    def search3(self,query): ######### spell checker
        query_as_list = self._parser.parse_query(query)  ### line 41  override the existing array without adding the query words
        query_spell_check=self.spell_checker(query_as_list)
        relevant_docs = self._relevant_docs_from_posting(query_spell_check)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        return n_relevant, ranked_doc_ids

    def search1(self,query): ######### thesarus and spell checker
        start = time.time()
        query_as_list = self._parser.parse_query(query)  ### line 41  override the existing array without adding the query words
        query_spell_check=self.spell_checker(query_as_list)
        query_as_list3 =self.thesaurus_synonyms(query_spell_check)
        relevant_docs = self._relevant_docs_from_posting(query_as_list3)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = Ranker.rank_relevant_docs(relevant_docs)
        end = time.time()
        return n_relevant, ranked_doc_ids


    def thesaurus_synonyms(self,query):
        arr=[]
        for token in query:
            t.synonyms(token)
            t.scored_synonyms(token)
            t.synonyms(token,fileid="simN.lsp")
            syn_words=list(t.synonyms(token,fileid="simN.lsp"))
            if token not in arr:
                arr.append(token)
            for syn in syn_words:
                if syn not in arr:
                    arr.append(syn)
        return arr



    def word_net_synonyms(self, query):
        synonyms = []
        for i in query:
            try:
                synonyms[i] = []
                for synset in wn.synsets(i):
                    for lemma in synset.lemmas():
                        val = synonyms[i]
                        if (lemma.name() not in val and "_" not in lemma.name()):
                            synonyms[i].append(lemma.name())
            except:
                    continue
        return synonyms

    def create_syno_arr_from_arr(self, arr):
        array=[]
        for i in arr:
            try:
                syno_arr = self._model.most_similar(i, topn=6)
                for syno in syno_arr:
                    if '@' in syno[0]:
                        continue
                    else:
                        array.append(syno[0])
            except:
               tmp=0
        for i in arr:
            array.append(i)
        return array

    def spell_checker(self,arr):
        array=[]
        for i in arr:
            if(i.lower() in self.spell_arr):
                array.append(i)
            else:
                array.append(self.spellcheck.correction(i.lower()))
        return array
