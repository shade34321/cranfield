import math
import string

from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from readers import read_queries, read_documents

inverted_index = defaultdict(lambda: defaultdict(int))
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
total_docs = 0


def remove_not_indexed_tokens(tokens):
    #Should work
    return [token for token in tokens if token in inverted_index]


def merge_two_postings(first, second):
    # first_index = 0
    # second_index = 0
    # merged_list = []
    # while first_index < len(first) and second_index < len(second):
    #     if first[first_index] == second[second_index]:
    #         merged_list.append(first[first_index])
    #         first_index = first_index + 1
    #         second_index = second_index + 1
    #     elif first[first_index] < second[second_index]:
    #         first_index = first_index + 1
    #     else:
    #         second_index = second_index + 1
    # return merged_list

    # Sets are a bag of words and guarantee uniqueness. This is a basic OR operation
    # This should probably be sortd but meh
    return first + list(set(second) - set(first))


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
        return merge_postings(indexed_tokens)


def tokenize(text):
    # This should be working but for some reason it's not. I'll come back later an figure out why.
    # Converting to lower case and splitting on space should be enough - Translate apparently doesn't work with unicode?
    # return text.translate(None, string.punctuation).lower().split(' ')
    text = ''.join(ch for ch in text if ch not in set(string.punctuation))
    return [ps.stem(word) for word in text.lower().split(' ') if word not in stop_words]

def term_freq(token, doc_id):
    return 1 + math.log(inverted_index[token][doc_id])

def idf(token):
    return math.log((total_docs - 1) / float(len(inverted_index[token])))

def add_token_to_index(token, doc_id):
    inverted_index[token][doc_id] += 1

def add_to_index(document):
    doc_info = [v for k, v in document.iteritems() if k not in ['id', 'author', 'bibliography', 'body']]
    for info in doc_info:
        for token in tokenize(info):
            add_token_to_index(token, document['id'])


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
