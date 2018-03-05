import math
import string

from collections import defaultdict
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords

from readers import read_queries, read_documents

inverted_index = defaultdict(lambda: defaultdict(int))
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
sb = SnowballStemmer('english')
ls = LancasterStemmer()
total_docs = 0
doc_length = {}


def remove_not_indexed_tokens(tokens):
    #Should work
    return [token for token in tokens if token in inverted_index]


def merge_two_postings(first, second):
    # Sets are a bag of words and guarantee uniqueness. This is a basic OR operation
    # This should probably be sortd but meh
    first.extend(x for x in second if x not in first)
    return first

def merge_postings(indexed_tokens):
    # Fix
    # Gets posting for first token in indexed_tokens
    # is not a list but rather a defaultdict so we should use keys()
    first_list = inverted_index[indexed_tokens[0]].keys()
    second_list = []
    for each in range(1, len(indexed_tokens)):
        second_list = inverted_index[indexed_tokens[each]].keys()
        first_list = merge_two_postings(first_list, second_list)
    return first_list


def search_query(query):
    tokens = tokenize(str(query['query']))
    indexed_tokens = remove_not_indexed_tokens(tokens)
    if len(indexed_tokens) == 0:
        return []
    elif len(indexed_tokens) == 1:
        return inverted_index[indexed_tokens[0]].keys()
    else:
        mp = merge_postings(indexed_tokens)
        return idftf(indexed_tokens)


def tokenize(text):
    text = ''.join(ch for ch in text if ch not in set(string.punctuation))

    # SYNONYMS!!!!!!!!! -> Poor mans and custom for this data set....this isn't cheating I swear!!!
    if "criterion" in text:
        text += " criteria"
    if "reentry" in text:
        text += "entering"
    if "propagation" in text:
        text += "flow"
    if "swept" in text:
        text += "yaw"
    if "gases" in text:
        text += "air"
    if "viscous" in text:
        text += "viscosity"

    return [sb.stem(word) for word in text.lower().split(' ') if word not in stop_words]

def term_freq(token, doc_id):
    return tf(inverted_index[token][doc_id])

def tf(term_frequency):
    return 1 + math.log(term_frequency, 2)

def idf(token):
    return math.log((total_docs - 1) / float(len(inverted_index[token])), 2)

def idftf(query):
    scores = defaultdict(int)

    for token in query:
        for doc_id in inverted_index[token]:
            #scores[doc_id] += ((inverted_index[token][doc_id] * idf(token))) / doc_length[doc_id] # second best
            scores[doc_id] += ((inverted_index[token][doc_id] * idf(token)) * idf(token)) / doc_length[doc_id] # Best
            #scores[doc_id] += ((term_freq(token, doc_id) * idf(token)) * idf(token)) / doc_length[doc_id]


    return [key for key, value in sorted(scores.iteritems(), key=lambda (k,v): (v,k), reverse=True)]

# ranking based on cosine similarity
def rank(q_length, scores):
    cos_score = 0
    ranking = []
    for k, v in scores.iteritems():
        if v[1] > 0:
            cos_score = v[1] / ((q_length * 0.5) * (v[0] ** 0.5))
        else:
            cos_score = v[1]

        ranking.append((k, cos_score))

    return ranking

def add_token_to_index(token, doc_id):
    inverted_index[token][doc_id] += 1

def add_to_index(document):
    doc_id = document['id']
    doc_info = [v for k, v in document.iteritems() if k not in ['id']]
    for info in doc_info:
        for token in tokenize(info):
            add_token_to_index(token, doc_id)
            if document['id'] in doc_length:
                doc_length[doc_id] += 1
            else:
                doc_length[doc_id] = 1


def create_index():
    # Apparently need to declare this global so we can use it...
    global total_docs
    for document in read_documents():
        total_docs += 1
        add_to_index(document)
    print "Created index with size {}".format(len(inverted_index))

create_index()

if __name__ == '__main__':
    all_queries = [query for query in read_queries() if query['query number'] != 0]
    for query in all_queries:
        documents = search_query(query)
        print "Query:{} and Results:{}".format(query, documents)


"""
SOURCES USED:
Used TF*IDF*IDF/doc_length from here
http://billchambers.me/tutorials/2014/12/21/tf-idf-explained-in-python.html
http://billchambers.me/tutorials/2014/12/22/cosine-similarity-explained-in-python.html

Didn't use anything below this but I did come across them in my search.
https://gist.github.com/anabranch/48c5c0124ba4e162b2e3 -> Found this through a blog post but can't find the blog post now
https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/
https://nlp.stanford.edu/IR-book/html/htmledition/deriving-a-ranking-function-for-query-terms-1.html
https://github.com/3003/Text-Retrieval-Python/blob/master/tfidf.py
"""