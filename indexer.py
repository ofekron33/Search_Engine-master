import numpy as np
import  utils
import math
from document import Document_to_index
# DO NOT MODIFY CLASS NAME
from gensim.models import KeyedVectors
from configuration import ConfigClass
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.vector_dictionary = {}
        self.inverted_idx = {}
        #self.model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True, limit=300000)
        #self.model = KeyedVectors.load_word2vec_format("D:\\Downloads\\modell3.bin", binary=True)
       # self.model = KeyedVectors.load_word2vec_format("model0601test1a.bin", binary=True)
        self.model=KeyedVectors.load_word2vec_format("model\\model0601test1a.bin", binary=True)
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
                self.inverted_idx[term] = [[document.tweet_id]]

            else:
                self.inverted_idx[term][0].append(document.tweet_id)
        self.postingDict[document.tweet_id] = (document.term_doc_dictionary, self.average_vector(document.term_doc_dictionary))
   #     self.postingVector[document.tweet_id] = self.average_vector(document.term_doc_dictionary)
        self.doc_num += 1


    def average_vector(self,dictionary):

        vector = np.zeros((300,))  ##init matrix [0,0,0,0......0 ->300 time]
        word_counter=0
        words = [word for word in dictionary if word in self.index_word_set]
        if len(words) >= 1:
            return np.mean(self.model[words], axis=0)
        else:
            return np.zeros((300,))
        # self.counter+=1
        # try:
        #     for word in dictionary:
        #         if word.lower() in self.vector_dictionary:
        #             vector=np.add(vector,self.vector_dictionary[word])
        #         elif word.lower() in self.index_word_set:
        #             self.vector_dictionary[word]=self.model[word]
        #             vector = np.add(vector, self.model[word])  ##adding vectors
        # except:
        #     tmp = 0
        # return vector
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
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
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        self.merge_dicts()

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



    def merge_dicts(self):
        merged_dict = {}
        for key in self.inverted_idx.keys():
            merged_dict[key] = self.inverted_idx[key]
        for key in self.postingDict.keys():
            merged_dict[key] = self.postingDict[key]
        utils.save_obj(merged_dict, "inverted_index")

    def end_indexer(self):
        self.merge_dicts()

        #utils.save_obj(self.postingVector,"vectors")
