
class Document:

    def __init__(self, tweet_id, tweet_date=None, full_text=None, url=None, retweet_text=None, retweet_url=None,
                 quote_text=None, quote_url=None, term_doc_dictionary=None, doc_length=0):
        """
        :param tweet_id: tweet id
        :param tweet_date: tweet date
        :param full_text: full text as string from tweet
        :param url: url
        :param retweet_text: retweet text
        :param retweet_url: retweet url
        :param quote_text: quote text
        :param quote_url: quote url
        :param term_doc_dictionary: dictionary of term and documents.
        :param doc_length: doc length
        """
        self.tweet_id = tweet_id
        self.tweet_date = tweet_date
        self.full_text = full_text
        self.url = url
        self.retweet_text = retweet_text
        self.retweet_url = retweet_url
        self.quote_text = quote_text
        self.quote_url = quote_url
        self.term_doc_dictionary = term_doc_dictionary
        self.doc_length = doc_length

class Document_to_index:
    __slots__ = ['tweet_id', 'term_doc_dictionary', 'max_tf', 'unique_words', 'tweet_length','hashtag_arr','__dict__']
    def __init__(self, tweet_id, term_doc_dictionary, max_tf, unique_words, tweet_length,hashtag_arr):
        self.tweet_id = tweet_id
        self.term_doc_dictionary = term_doc_dictionary
        self.max_tf = max_tf
        self.unique_words = unique_words
        self.tweet_length = tweet_length
        self.hashtag_arr=hashtag_arr
