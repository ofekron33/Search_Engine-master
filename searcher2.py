import math
import numpy as np
from scipy import spatial
import nltk
from nltk.corpus import wordnet as wn
from ranker import Ranker
import utils


# DO NOT MODIFY CLASS NAME
class Searcher2:
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
        query_as_list = self._parser.parse_query(query)
        word_net_syno=self.word_net_synonyms(query_as_list.keys())
        query_final={}
        for key in query_as_list.keys():
            query_final[key]=(query_as_list[key],word_net_syno[key])
        relevant_docs = self._relevant_docs_from_posting(query_final) ##dictionary, key=word,value=tuple
                                                                    #tuple(0)=frequency, tuple(1)=array of synonyms.
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
        for term in query_as_list.keys():
            tweet_arr = self._indexer.inverted_idx[term][1]
            for tup in tweet_arr:
                tweet_id = tup[1]
                relevant_docs[tweet_id] = [0,0,0]
                relevant_docs[tweet_id][0] = self.CossimVectors(query_as_list,self._indexer.inverted_idx[tweet_id][0])
                relevant_docs[tweet_id][1] = self.Word2VecSim(query_as_list,self._indexer.postingVector[tweet_id])
                print(relevant_docs[tweet_id][0])
                print(relevant_docs[tweet_id][1])
                relevant_docs[tweet_id][2] = (relevant_docs[tweet_id][0]+relevant_docs[tweet_id][1])/2
        return relevant_docs

    def average_vector(self, dictionary):
        vector = np.zeros((300,))  ##init matrix [0,0,0,0......0 ->300 time]
        word_counter = 0

        try:
            for word in dictionary:
                if word in self.vector_dictionary:
                    vector = np.add(vector, self.vector_dictionary[word])
                elif word in self.index_word_set:
                    word_counter += 1
                    self.vector_dictionary[word] = self.model[word]
                    vector = np.add(vector, self.model[word])  ##adding vectors
            if (word_counter > 0):
                vector = np.divide(vector, word_counter)

            else:
                return np.zeros((300,))
        except:
            tmp = 0
        return vector


    def Word2VecSim(self,query,doc):

        zero_vector = np.zeros((300,))
        query_vector = self.average_vector(query)

        if np.array_equal(zero_vector, doc):
            return 0
        else:
            return 1 - spatial.distance.cosine(doc, query_vector)


    def CossimVectors(self,query,doc):
        return self.numer(query,doc)/self.denumer(query,doc)

    def numer(self, query, doc):
        num = 0
        for term in query.keys():
            num += query[term]*doc[term]
        return num


    def denumer(self, query , doc):
        denum = 0
        for term in doc.keys():
            denum += doc[term]^2
        denum = math.sqrt(denum)*math.sqrt(len(query))
        return denum
    def word_net_synonyms(self,query):
        from nltk.corpus import wordnet as wn
        synonyms = {}
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