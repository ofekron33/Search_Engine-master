import numpy as np
import utils
import configuration
from gensim.models import KeyedVectors
import os
class Indexer:
    def __init__(self, config):
        self.vector_dictionary = {}
        self.inverted_idx = {}
        self.model =config._model


        self.postingDict = {}
        self.postingVector = {}
        self.index_word_set = self.model.wv.index2word
        self.config = config
        self.doc_num = 0
        self.counter = 0
  

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
                self.inverted_idx[term] = [[document.tweet_id]]

            else:
                self.inverted_idx[term][0].append(document.tweet_id)
        dicLen = len(document_dictionary)
        if dicLen >=12:
            self.postingDict[document.tweet_id] = [document.term_doc_dictionary, self.average_vector(document.term_doc_dictionary),1]
        else:
            self.postingDict[document.tweet_id] = [document.term_doc_dictionary,0, 0]
        self.doc_num += 1


    def average_vector(self,dictionary):

        vector = np.zeros((300,))  ##init matrix [0,0,0,0......0 ->300 time]
        word_counter=0
        words = [word for word in dictionary if word in self.index_word_set]
        if len(words) >= 1:
            return np.mean(self.model[words], axis=0)
        else:
            return np.zeros((300,))

    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        diction = utils.load_obj(fn)
        self.inverted_idx = {}
        self.postingDict = {}
        for key in diction.keys():
            if len(diction[key]) == 2:
                self.postingDict[key] = diction[key]
            else:
                self.inverted_idx[key] = diction[key]
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        self.merge_dicts()

    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []



    def merge_dicts(self):
        merged_dict = {}
        for key in self.inverted_idx.keys():
            merged_dict[key] = self.inverted_idx[key]
        for key in self.postingDict.keys():
            merged_dict[key] = self.postingDict[key]
        utils.save_obj(merged_dict, "idx_bench")


    def end_indexer(self):
        self.merge_dicts()

