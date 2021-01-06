import numpy as np
import  utils
import math
from document import Document_to_index
# DO NOT MODIFY CLASS NAME
from gensim.models import KeyedVectors

class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.vector_dictionary = {}
        self.inverted_idx = {}
        self.model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True, limit=300000)
        self.postingDict = {}
        self.postingVector = {}
        self.index_word_set = self.model.wv.index2word
        self.config = config
        self.doc_num=0
        self.counter = 0
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        max_tf = document.max_tf
        if max_tf == 0:
            return

        uniqueCounter = document.unique_words
        #        tweet_length = len(document.full_text)
        for term in document_dictionary.keys():  # in the inverted index we have list of tweet tuples with tf with pointer to appropriate file
            if term not in self.inverted_idx.keys():
                self.inverted_idx[term] = [[1, -1, document_dictionary[term]],[]]
                self.inverted_idx[term][1].append((document_dictionary[term] / max_tf, document.tweet_id))
            else:
                self.inverted_idx[term][0][0] += 1
                self.inverted_idx[term][0][2] += document_dictionary[term]
                self.inverted_idx[term][1].append((document_dictionary[term] / max_tf, document.tweet_id))
        self.postingDict[document.tweet_id] = (document.term_doc_dictionary, document.max_tf, document.hashtag_arr,self.average_vector(document.term_doc_dictionary))
   #     self.postingVector[document.tweet_id] = self.average_vector(document.term_doc_dictionary)
        self.doc_num += 1


    def average_vector(self,dictionary):

        vector = np.zeros((300,))  ##init matrix [0,0,0,0......0 ->300 time]
        word_counter=0

        self.counter+=1
        try:
            for word in dictionary:
                if word in self.vector_dictionary:
                    vector=np.add(vector,self.vector_dictionary[word])
                elif word in self.index_word_set:
                    self.vector_dictionary[word]=self.model[word]
                    vector = np.add(vector, self.model[word])  ##adding vectors
        except:
            tmp = 0
        return vector
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self.inverted_idx = utils.load_obj(fn)
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        utils.save_obj(fn,"idx_bench")

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def IDF(self):
        for key in self.inverted_idx.keys():
            if(key=="bioweapon"):
                tmp=22
                tmp1=self.inverted_idx[key]
            idf = self.doc_num/self.inverted_idx[key][0][0]
            idf = math.log(idf,2)
            self.inverted_idx[key][0][1] = idf

    def merge_dicts(self):
        merged_dict = {}
        for key in self.inverted_idx.keys():
            merged_dict[key] = self.inverted_idx[key]
        for key in self.postingDict.keys():
            merged_dict[key] = self.postingDict[key]
        self.inverted_idx = merged_dict
        self.postingDict = {}
    def end_indexer(self):
        self.IDF()
        self.merge_dicts()
        utils.save_obj(self.inverted_idx,"idx_bench")
        #utils.save_obj(self.postingVector,"vectors")
