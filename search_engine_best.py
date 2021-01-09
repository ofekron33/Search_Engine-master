import time

import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
from gensim.models import KeyedVectors
import csv
import os
import utils


# DO NOT CHANGE THE CLASS NAME



class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config=None)
        #self.model =KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True, limit= 20000)
        #self.model = KeyedVectors.load_word2vec_format("D:\\Downloads\\modell3.bin", binary=True)
        self.model = config.get_download_model()
        self.num_doc=0

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        number_of_documents = 0
        start = time.time()
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            number_of_documents += 1
            self.num_doc+=1

            # index the document data
            self._indexer.add_new_doc(parsed_document)

        end = time.time()

        self._indexer.end_indexer()
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and 
        assign to self._model, which is passed on to the searcher at query time.
        """


        # DO NOT MODIFY THIS SIGNATURE
        # You can change the internal implementation as you see fit.

    def search(self, query):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
       # searcher = Searcher(self._parser, self._indexer, model=self.model)
        searcher = Searcher(self._parser, self._indexer, model=self.model)

        return searcher.search(query)

    @property
    def indexer(self):
        return self._indexer


def main():  # (corpus_path,output_path,stemming,queries,num_docs_to_retrieve):
    pass


def get_all_parquet_files(dir):
    arr=[]
    for r, d, f in os.walk(dir):
        for file in f:
            if file.endswith(".parquet"):
                # print(os.path.join(r, file))
                arr.append(os.path.join(r, file))
    return arr

