import time

import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
from gensim.models import KeyedVectors
import os
import utils


# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        #self.model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True, limit=200000)
    #    self.model = KeyedVectors.load_word2vec_format("D:\\Downloads\\modell3.bin", binary=True)
        self.model = KeyedVectors.load_word2vec_format("D:\\Downloads\\model0601test1a.bin", binary=True)

        self._indexer = Indexer(self.model)

        self.num_doc=0
        self.efk=0;
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
            print(number_of_documents)
            # index the document data
            self._indexer.add_new_doc(parsed_document)

        utils.save_obj(self._indexer.inverted_idx,"idx_bench")

        utils.save_obj(self._indexer.postingVector,"postingVec")
        end = time.time()
        print("time took - "+str(end-start))

        print('Finished parsing and indexing.')
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
        pass

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

def main():  # (corpus_path,output_path,stemming,queries,num_docs_to_retrieve):
    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    #arr1=get_all_parquet_files("D:\Downloads\Data")
    arr2=get_all_parquet_files(os.getcwd())
    s=SearchEngine()
    s.build_index_from_parquet(arr2[3])
    # s.search("Covid")


def get_all_parquet_files(dir):
    arr=[]
    for r, d, f in os.walk(dir):
        for file in f:
            if file.endswith(".parquet"):
                print(os.path.join(r, file))
                arr.append(os.path.join(r, file))
    return arr

    #     #  config = ConfigClass(corpus_path,output_path,stemming)   # while True:
    #     config = ConfigClass('D:\\Downloads\\Data\\Data', "C:\\Users\\ofekr\\Search_Engine", False)  # while True:
    #     counter = run_engine(config)
    #     index_documents(counter, config)
    #     # freq_dict = index_documents(counter,stemming)
    #     merge_files(counter, config)
    #     # num_of_files=merge_files(counter)
    #     inverted_index = utils.load_inverted_index(config.output_path)  ##output path
    #     # query = input("Please enter a query: ")
    #     # k = int(input("Please enter number of docs to retrieve: "))
    #     # inverted_index = load_index()
    # # queries=["Donalnd trump"]