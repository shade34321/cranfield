import collections
import math

from readers import read_relevance, read_queries
from search import search_query

query_document_relevance = {}
ideal_ndcg = {}

'''
DO NOT MODIFY THIS CLASS.
'''


def ideal_ndcg_queries():
    query_relevance = {}
    for relevance in read_relevance():
        query_id = relevance['query_num']
        doc_id = relevance['id']
        position = 5 - relevance['position']
        query_document_relevance[str(query_id) + "_" + str(doc_id)] = position
        if query_id in query_relevance:
            query_relevance[query_id].append(position)
        else:
            query_relevance[query_id] = [position]

    for key, value in query_relevance.items():
        sorted_relevance = sorted(query_relevance[key], reverse=True)
        count = 1
        sum = 0.0
        for each in sorted_relevance:
            sum = sum + each / math.log10(count + 1)
            count = count + 1
        ideal_ndcg[str(key)] = sum


def calculate_dcg(query, documents):
    count = 1
    sum = 0.0
    for document in documents:
        relevance =0
        key = str(query['query number']) + "_" + str(document)
        if key in query_document_relevance:
            relevance = query_document_relevance[key]
        sum = sum + relevance / math.log10(count + 1)
        count = count + 1
    return sum


if __name__ == '__main__':
    ideal_ndcg_queries()
    sum = 0.0
    all_queries = [query for query in read_queries() if query['query number'] != 0]
    scores = {0: {}, 10:{}, 20:{}, 30: {}, 40: {}, 50: {}, 60: {}, 70: {}, 80: {}, 90: {}, 100: {}}

    for query in all_queries:
        documents = search_query(query)
        assert len(documents)==len(set(documents)), "Search results should not have duplicates:"+str(documents)
        if len(documents) > 0:
            dcg = calculate_dcg(query, documents)
            idcg = ideal_ndcg[str(query['query number'])]
            ndcg = dcg / idcg

            if ndcg >= 1:
                scores[100][query['query number']] = ndcg
                #print "Query:{}".format(query)
                #print "dcg={}, ideal={}, ndcg={}".format(dcg, idcg, ndcg)
            elif ndcg >= .9:
                scores[90][query['query number']] = ndcg
                #print "Query {}".format(query)
            elif ndcg >= .8:
                scores[80][query['query number']] = ndcg
            elif ndcg >= .7:
                scores[70][query['query number']] = ndcg
            elif ndcg >= .6:
                scores[60][query['query number']] = ndcg
            elif ndcg >= .5:
                scores[50][query['query number']] = ndcg
            elif ndcg >= .4:
                scores[40][query['query number']] = ndcg
            elif ndcg >= .3:
                scores[30][query['query number']] = ndcg
            elif ndcg >= .2:
                scores[20][query['query number']] = ndcg
            elif ndcg >= .1:
                scores[10][query['query number']] = ndcg
                #print "Query:{} and Results:{}".format(query, documents)
                #print "dcg={}, ideal={}, ndcg={}".format(dcg, idcg, ndcg)
                #print "Query {}".format(query)
            else:
                scores[0][query['query number']] = ndcg
                #print "Query {}".format(query)


            sum = sum + ndcg
    print "Final ncdg for all queries is {}".format(sum / len(all_queries))

    histogram = collections.OrderedDict(sorted(scores.items(), key=lambda k: k[0]))
    for k,v in histogram.items():
        print "We have {} scores in {}-{}".format(len(v), k, k + 10)
        #for query_num, ndcg_score in v.iteritems():
        #    print "Query Num: {} NDCG: {}".format(query_num, ndcg_score)