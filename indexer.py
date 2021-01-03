from document import Document_to_index
# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = config
        self.doc_num=0
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
        self.postingDict[document.tweet_id]=(document.term_doc_dictionary,document.max_tf,document.hashtag_arr)
        self.doc_num += 1

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        raise NotImplementedError

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        raise NotImplementedError

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
