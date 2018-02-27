import math
import string

from collections import defaultdict
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords

from readers import read_queries, read_documents

inverted_index = defaultdict(lambda: defaultdict(int))
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
sb = SnowballStemmer('english')
total_docs = 0
doc_length = {}


def remove_not_indexed_tokens(tokens):
    #Should work
    return [token for token in tokens if token in inverted_index]


def merge_two_postings(first, second):
    # Sets are a bag of words and guarantee uniqueness. This is a basic OR operation
    # This should probably be sortd but meh
    #return first + list(set(second) - set(first))
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
        #return merge_postings(indexed_tokens)
        return idftf(indexed_tokens)


def tokenize(text):
    # Converting to lower case and splitting on space should be enough - Translate apparently doesn't work with unicode?
    # I used both porterstemming and snowball stemming. They both had the same affect on the score.
    #Snowball is what I used last and hence why it's here. 
    text = ''.join(ch for ch in text if ch not in set(string.punctuation))
    #return [ps.stem(word) for word in text.lower().split(' ') if word not in stop_words]
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
            scores[doc_id] += ((term_freq(token, doc_id) * idf(token)) * idf(token)) / doc_length[doc_id]


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