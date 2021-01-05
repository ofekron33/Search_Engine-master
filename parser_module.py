import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from math import log
from document import Document_to_index
import urllib3
import spacy
class Parse:

    def __init__(self):
        self.counter=0
        self.stop_words = frozenset(stopwords.words('english'))
        self.added_stop_words=["I","The","rT","RT","rt","http","https",'t.co'," ","","twitter.com","-","www","_","&amp","##","###","####","#####","19"]
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
  #      doc=self.nlp(txt1)
  #      doc_test=self.nlp(text)
   #     entity=[]
    #    entity_test=[]
     #   for e in doc.ents:
      #      if(e.text not in entity):
       #         entity.append(e.text)
       # for e in doc_test.ents:
        #    if(e.text not in entity):
         #       entity_test.append(e.text)
        terms=txt1.split()
        index=0
        while(index<len(terms)):
        #    w=terms[index].lower()
            usa_abbrev=self.usa_abbreviations.get(terms[index].upper(),"Never")
            if(terms[index] in self.stop_words or terms[index] in  self.added_stop_words):
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
        # return terms

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
        full_text = doc_as_list[2]
        pattern = re.compile("(?P<url>https?://[^\s]+)", re.S)
        full_text_without_url = re.sub(pattern, "", full_text)
        all_uppercase_text = bool(re.match(r'[a-z\s]+$', full_text_without_url))  ##if all text is uppercase lower it.
        if (all_uppercase_text == False):
            full_text_without_url.lower()

        self.parse_sentence(full_text_without_url)


        if (len(self.dic) > 0):
            max_tf = max(self.dic.values())
            unique_words = len(self.dic.keys())
        else:
            max_tf = 0
            unique_words = 0

        url = doc_as_list[3]
        if (url is not None) and (url != '{}'):
            if (len(url) > 2):
                tmp = url.split('"')
                for url in tmp:
                    if ("http" in url):
                        tok_url = self.parse_url(url)
                        for term in tok_url:
                            if (term != "''" or term != "," and len(term) >= 1):
                                self.enter_dic(term)
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        if (retweet_url is not None) and ("http" in retweet_url):
            if (len(url) > 2):
                tmp = url.split('"')
                for url in tmp:
                    if ("http" in url):
                        tok_url = self.parse_url(url)
                        for term in tok_url:
                            self.enter_dic(term.lower())
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        if (quote_url is not None) and ("http" in quote_url):

            #     tmp = quote_url.partition("https")[1] + quote_url.partition("https")[2]
            u = re.findall("(?P<url>https?://[^\s]+)", quote_url)
            for match in u:
                tok_url = self.parse_url(match)
                for term in tok_url:
                    self.enter_dic(term.lower())
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

    # def handle_full_text(self,full_text): ##removes url from full_text and check if all of the text in caps lock.
    #     pattern = re.compile("(?P<url>https?://[^\s]+)", re.S)
    #     full_text_without_url=re.sub(pattern,"",full_text)
    #     all_uppercase_text= bool(re.match(r'[a-z\s]+$', full_text_without_url)) ##if all text is uppercase lower it.
    #     if (all_uppercase_text == False):
    #         full_text_without_url.lower()
    #     self.parse_sentence(full_text_without_url)
    #     return full_text_without_url

    def enter_dic(self,term):
        if(term not in self.stop_words or term not in self.added_stop_words):
            if(term not in self.dic.keys()):
                self.dic[term]=1
            else:
                self.dic[term]+=1

    def parse_url(self, url):
        """
              This function tokenize a given url
              :param text:
              """
        parsed_url = urllib3.util.parse_url(url)
        arr = []
        # pattern = re.compile("(?P<url>https?://[^\s]+)", re.S)
        # u = re.findall("(?P<url>https?://[^\s]+)", url)
        # for match in u:
        #    tok_url = self.parse_url(match)
        arr.append(parsed_url.scheme)  # https
        h = parsed_url.host
        if (h is not None):
            host = parsed_url.host
            if (host[0] == 'w'):
                h = urllib3.util.split_first(host, '.')
                for i in h:
                    if (i != '.'):
                        #      if(i  not in self.stop_words):
                        arr.append(i)
            else:
                arr.append(host)

        p = parsed_url.path
        if (p is not None):
            path = parsed_url.path.split('/')  # should be the path(after the .com and until the last /
            for i in path:
                if (i != ''):
                    if ("-" in i):
                        tmp = i.split('-')
                        for j in tmp:
                            arr.append(j)
                else:
                    arr.append(i)
            #     if (i not in self.stop_words):

        q = parsed_url.query
        if (q is not None):
            query = parsed_url.query.split('=')
            for i in query:
                #    if (i not in self.stop_words):
                arr.append(i)
        return arr
    def parse_query(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        dic={}
        txt1 = self.multiple_replace(text)
        terms = txt1.split()
        index = 0
        while (index < len(terms)):
            #    w=terms[index].lower()
            usa_abbrev = self.usa_abbreviations.get(terms[index].upper(), "Never")
            if (terms[index] in self.stop_words):
                index = index + 1
                continue
            elif (terms[index][0] == '@' and len(terms[index]) > 1):  # @rule
                    if (terms[index] not in dic.keys()):
                        dic[terms[index]]= 1
                    else:
                        dic[terms[index]] += 1
                    index = index + 1
                    continue
            elif (terms[index][0] == '#'):  # #rule
                lst = self.parse_hashtag(terms[index])
                for i in lst:
                    if (i not in dic.keys()):
                        dic[terms[index]] = 1
                    else:
                        dic[terms[index]] += 1
                    index = index + 1
                    continue
                index = index + 1
            elif (((usa_abbrev != "Never") )):
                if (terms[index].upper() not in dic.keys()):
                    dic[terms[index]] = 1
                    if(usa_abbrev not in dic.keys()):
                        dic[usa_abbrev]=1
                    else:
                        dic[usa_abbrev]+=1
                else:
                    dic[terms[index]] += 1
                    if (usa_abbrev not in dic, keys()):
                        dic[usa_abbrev] == 1
                    else:
                        dic[usa_abbrev] += 1
                index = index + 1
                continue
                if (usa_abbrev not in dic.keys()):
                    dic[usa_abbrev] = 1
                else:
                    dic[usa_abbrev] += 1
                index = index + 1
                continue
            elif (terms[index].isdigit()) or (re.search(r"(?:\\d+\\s+)?\\d/\\d", terms[index])) or (
            re.search(r'^-?[0-9]+\/[0-9]+$', terms[index])):
                if (index == len(terms) - 1):  ##mikre katze doc24512 (# in last token)#case 0 the number is the last index
                    w = self.parse_numbers(terms[index], '')
                    if (w not in dic.keys()):
                        dic[w] = 1
                    else:
                        dic[w] += 1
                    index = index + 1
                else:
                    word_check = terms[index + 1].lower()
                    if (word_check == '%' or word_check == 'percent' or word_check == 'percentage' or word_check == 'million' or word_check == 'thousand' or word_check == 'billion'):
                        w = self.parse_numbers(terms[index], terms[index + 1])
                        if (w not in dic.keys()):
                            dic[w] = 1
                        else:
                            dic[w] += 1

                        index = index + 2
                    else:
                        w = self.parse_numbers(terms[index], '')
                        if (w not in dic.keys()):
                            dic[w] = 1
                        else:
                            dic[w] += 1
                        index = index + 1
            else:
                if (terms[index]not in dic.keys()):
                    dic[terms[index]] = 1
                else:
                    dic[terms[index]] += 1
                index = index + 1
        return dic
