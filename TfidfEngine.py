from typing import overload

from gensim import corpora,models,similarities
from collections import defaultdict
from StringMatcher import StringMatcher
import re, string;
from collections import deque
from AbstractEngine import AbstractSearchEngine
from copy import deepcopy


class TfidfEngine(AbstractSearchEngine):

    # take 1..N ngrams into account
    MAX_NGRAM = 3

    # maximum levenshtein distance between misspelled ngram(word/phrase) and ngram in corpus
    # will correct given number of mistakes, ngrams with same distance share weight
    MAX_LEVENSHTEIN_DISTANCE = 4

    def __init__(self):
        super(TfidfEngine, self).__init__()
        # models.TfidfModel object
        self._tfidf = None
        # similarities.SparseMatrixSimilarity object
        self._index = None
        # defaultdict
        self._dictionary = None

        self._subengines = {}

    def search(self, search_string, nmax=MAX_NGRAM):
        self._tmp_dict = {}
        actual_max = min(nmax, len(self.make_bag(search_string,n=1)))
        #print (actual_max)
        for nmax in range(1,actual_max+1):
            self._search(search_string, n=nmax)
        dd={}
        for k in sorted(self._tmp_dict,key=self._tmp_dict.get):
            yield (k,self._tmp_dict[k])

    def _search(self, search_string, n):
        self._tfidf, self._index, self._dictionary = self._subengines[n]
        bag = self.make_bag(search_string,n=n)
        vector = self._wordlist_to_tokens_vector(bag)
        sims = self._index[self._tfidf[vector]]
        matches=dict(enumerate(sims))
        # sorted
        smatches = sorted(matches,key=matches.get)
        for id in smatches:
            if matches[id]==0:
                continue
            if id in self._tmp_dict:
                self._tmp_dict[id]+=matches[id]
            else:
                self._tmp_dict[id] = matches[id]

    def prepare(self):
        for i in range(1, TfidfEngine.MAX_NGRAM+1):
            self._prepare(ngram=i)
            #self._subengines[i] = deepcopy(self._tfidf), deepcopy(self._index), deepcopy(self._dictionary)
            self._subengines[i] = self._tfidf, self._index, self._dictionary
        print(self._subengines)
    def _prepare(self,ngram=1):
        texts = [[word for word in self.make_bag(document, n=ngram)] for document in self._documents]
        frequency = defaultdict(int)

        for text in texts:
            for token in text:
                frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 0]
                  for text in texts]
        # for k in frequency:
        #     print(k, frequency[k])
        dictionary = corpora.Dictionary(texts)
        vectorized = []
        for doc in self._documents:
            vectorized.append(dictionary.doc2bow(self.make_bag(doc, n=ngram)))

        self._tfidf = models.TfidfModel(vectorized)
        self._index = similarities.SparseMatrixSimilarity(self._tfidf[vectorized], num_features=len(dictionary.keys()))
        self._dictionary = dictionary

    def _wordlist_to_tokens_vector(self, wordlist):
        vec = []
        for word in wordlist:
            try:
                vec.append((self._dictionary.token2id[word], 1))
            except KeyError as e:
                matches = self.best_match(word)
                print (len(matches))
                print (matches)
                if len(matches)==0 or matches[0]==None:
                    continue
                for bb in matches:
                    print(bb, self._dictionary[bb])
                    vec.append((bb, 1.0/len(matches)))
                print (len(matches))
        return vec

    def best_match(self, word):
        print(word)
        matcher = StringMatcher()
        matcher.set_seq1(word)
        min_dist = (TfidfEngine.MAX_LEVENSHTEIN_DISTANCE, [None])

        for token, id in self._dictionary.token2id.items():
            matcher.set_seq2(token)
            if matcher.distance() < min_dist[0]:
                min_dist = (matcher.distance(), [id])
            elif matcher.distance() == min_dist[0]:
                min_dist[1].append(id)
        from pprint import pprint; pprint(min_dist)
        return min_dist[1]

