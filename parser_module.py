import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from math import log
from document import Document_to_index
import urllib3

class Parse:

    def __init__(self):
        self.counter=0
        self.stop_words = frozenset(stopwords.words('english'))
        self.added_stop_words=["I","The","rT","rt","http","https",'t.co',"twitter.com","-","www","_","&amp","##","###","####","#####"]
        self.check=0
        self.words = open(r'zif.txt').read().split()
        self.dictionay_word_cost = dict((k, log((i + 1) * log(len(self.words)))) for i, k in enumerate(self.words))
        self.max_word_length = max(len(x) for x in self.words)
        self.dic={}
        self.hashtag_arr=[]
        self.usa_abbreviations = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
                                  "CA": "California",
                                  "CT": "Connecticut", "DC": "Washington DC", "DE": "Deleware", "FL": "Florida",
                                  "GA": "Georgia", "HI": "Hawaii", "IL": "Illinios", "IA": "Iowa",
                                  "KS": "Kansas", "KY": "Kentucky", "MD": "Maryland", "MA": "Massachusetts",
                                  "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
                                  "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
                                  "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
                                  "Covid": "cornavirus", "COVID": "cornavirus", "covid19": "cornavirus",
                                  "Covid19": "cornavirus", "Covid-19": "cornavirus", "covid-19": "cornavirus",
                                  "CORONAVIRUS": "cornavirus", "Coronavirus": "cornavirus", "Corona": "cornavirus",
                                  "Corona": "cornavirus", "corona": "cornavirus", "CORONA": "coronavirus",
                                  "COVID19": "coronavirus", "COVID-19": "cornavirus",
                                  "ND": "North Dakota", "OH": "Ohio", "PA": "Pennsylvania", "RI": "Rhode Island",
                                  "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
                                  "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virgina", "WA": "Washington",
                                  "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "USA": "United States",
                                  "IG": "Instagram", "FB": "Facebook"}

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        txt1=self.multiple_replace(text)
        terms=txt1.split()
        index=0
        while(index<len(terms)):
        #    w=terms[index].lower()
            usa_abbrev=self.usa_abbreviations.get(terms[index].upper(),"Never")
            if(terms[index] in self.stop_words):
                index=index+1
                continue
            elif (terms[index][0] == '@' and len(terms[index])>1):  # @rule
                    self.enter_dic(terms[index])
                    index = index + 1
                    continue
            elif (terms[index][0] == '#'):  # #rule
                lst=self.parse_hashtag(terms[index])
                for i in lst:
                    self.enter_dic(i.lower())
                    if(i not in self.stop_words and i not in self.hashtag_arr):
                        self.hashtag_arr.append(i)
                index=index+1
            elif (usa_abbrev!="Never"):
                self.enter_dic(terms[index].upper())
                self.enter_dic(usa_abbrev)
                index=index+1
            elif (terms[index].isdigit()) or (re.search(r"(?:\\d+\\s+)?\\d/\\d", terms[index])) or (re.search(r'^-?[0-9]+\/[0-9]+$', terms[index])):
                if (index == len(terms)-1): ##mikre katze doc24512 (# in last token)#case 0 the number is the last index
                         w=self.parse_numbers(terms[index],'')
                         self.enter_dic(w)
                         index=index+1
                else:
                    word_check=terms[index+1].lower()
                    if(word_check=='%' or word_check=='percent' or word_check=='percentage' or word_check=='million'  or word_check=='thousand' or word_check=='billion'):
                        w =self.parse_numbers(terms[index],terms[index+1])
                        self.enter_dic(w)
                        index=index+2
                    else:
                        w = self.parse_numbers(terms[index],'')
                        self.enter_dic(w)
                        index = index + 1
            else:
                self.enter_dic(terms[index])
                index = index + 1

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-presenting the tweet.
        :return: Document object with corresponding fields.
        """
        self.dic={}
        self.hashtag_arr=[]
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = self.handle_full_text(doc_as_list[2])

        if (len(self.dic) > 0):
            max_tf = max(self.dic.values())
            unique_words = len(self.dic.keys())
        else:
            max_tf = 0
            unique_words = 0

        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]

        doc_length =len(full_text)


       # document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,quote_url, term_dict, doc_length)
        document_to_index= Document_to_index(tweet_id,self.dic,max_tf,unique_words,doc_length,self.hashtag_arr)
        #print(str(self.counter)+",",self.hashtag_arr)
        return document_to_index

    def parse_numbers(self,index, next_index):
        value = ['', 'K', 'M', 'B']
        if bool(re.search(r'^-?[0-9]+\/[0-9]+$', next_index)) and float(index) < 1000:
            return index + ' ' + next_index
        if bool(re.search(r'^-?[0-9]+\/[0-9]+$', index)):
            return index
        elif(next_index.lower()=='%' or next_index.lower()=='percent' or next_index.lower()=='percentage'):
            return index +"%"
        elif (next_index.lower() =="billion") and float(index) < 1000:
            return index + "B"
        elif (next_index.lower() == "million"  and float(index) < 1000):
            return index + "M"
        elif (next_index.lower() == "thousand") and float(index) < 1000:
            return index + "K"
        number = float(index)
        size = 0
        while abs(number) >= 1000:
            size = size+1
            number /= 1000.0
            if size >= 3:
                break
        return str("%.3f" % number).strip("0").strip(".") + '' + str(value[size])

    def parse_hashtag(self, string):
        exp = []
        exp.append(string)
        if (len(string) == 1):  ##mikre katze doc24512 (# in last token)
            exp.append('number')  # adding number
            return exp
        word = string[1:]
        usa_abbrev = self.usa_abbreviations.get(word.upper(), "Never")
        list_tmp = []
        if (word.isalpha()) and (word.isupper() or word.islower()):
            if (usa_abbrev != "Never"):
                list_tmp.append(usa_abbrev)
                list_tmp.append(word)
            else:
                w = word.lower()
                list_tmp = self.conclude_space(w)
        else:
            list_tmp = self.parse_hastag_easy_case(word)
        for i in list_tmp:
            if (i != ''):
                exp.append(i)
        return exp

    def parse_hastag_easy_case(self, text):
        return [i for i in re.split(r"_|([A-Z][a-z]+)", text) if i]

    def conclude_space(self, string):
        def best_match(index):
            candidates = enumerate(reversed(cost_arr[max(0, index - self.max_word_length):index]))
            return min((c + self.dictionay_word_cost.get(string[index - k - 1:index], 999999999), k + 1) for k, c in
                       candidates)

        # Build the cost array.
        cost_arr = [0]
        for index in range(1, len(string) + 1):
            c, k = best_match(index)
            cost_arr.append(c)

        res = []
        length = len(string)
        while (length > 0):
            c, k = best_match(length)
            #   assert c == cost[length]
            res.append(string[length - k:length])
            length = length - k
        word = " ".join(reversed(res))
        return word.split()

    def multiple_replace(self, text):
        def cap(match):
            return match.group().lower()

        first_strip = re.sub("[’'`']", '', text)
        p = re.compile(r'((?<=[\.\?!:\W]\s)(\w+)|(^\w+))')  ##change uppercase after new sentence
        second_strip = p.sub(cap, first_strip)
        third_strip = re.sub(r"(?<!\d)\.|\.(?!\d)", '', second_strip)
        forth_strip = re.sub('[^A-Za-z0-9@#_$%]+', ' ', third_strip)
        return forth_strip

    def handle_full_text(self,full_text): ##removes url from full_text and check if all of the text in caps lock.
        pattern = re.compile("(?P<url>https?://[^\s]+)", re.S)
        full_text_without_url=re.sub(pattern,"",full_text)
        all_uppercase_text= bool(re.match(r'[a-z\s]+$', full_text_without_url)) ##if all text is uppercase lower it.
        if (all_uppercase_text == False):
            full_text_without_url.lower()
        self.parse_sentence(full_text_without_url)
        return full_text_without_url

    def enter_dic(self,term):
        if(term not in self.stop_words or term not in self.added_stop_words):
            if(term not in self.dic.keys()):
                self.dic[term]=1
            else:
                self.dic[term]+=1
        return