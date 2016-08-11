from typing import overload
from gensim import corpora,models,similarities
from collections import defaultdict
from StringMatcher import StringMatcher
from AbstractEngine import AbstractSearchEngine
import unittest

class TfidfEngine(AbstractSearchEngine):

    # take 1..N ngrams into account (maximum)
    MAX_NGRAM = 3

    # maximum levenshtein distance between misspelled ngram(word/phrase) and ngram in corpus
    # will correct given number of mistakes
    # ngrams with same distance share weight
    MAX_LEVENSHTEIN_DISTANCE = 2

    def __init__(self):
        super(TfidfEngine, self).__init__()
        # models.TfidfModel object
        self._tfidf = None
        # similarities.SparseMatrixSimilarity object
        self._index = None
        # defaultdict
        self._dictionary = None
        # for each N value we prepare engine containing only Ngrams
        # then similiarity value is sum of N results (from each subengine)
        self._subengines = {}

        # maps position in tfidf model to 
        # key which user specified when putting documents in as dictionary
        self._position_key_map = {}

    def find_best_match(self, search_string, *args, **kwargs):
        ''' returns key of document that fits best '''
        for k,_ in self.search(search_string, *args, **kwargs):
            return k

    def search(self, search_string, nmax=MAX_NGRAM):
        ''' searches through whole corpus
            returns generator object returning 2-tuples:
            - document's key for which similarity value is greater than 0
            - similarity value
        '''  
        # dict stores and adds value from each subengine run
        self._tmp_dict = {}
        actual_max = min(nmax, len(self.make_bag(search_string,n=1)))
        for nmax in range(1,actual_max+1):
            self._search(search_string, n=nmax)

        for k in sorted(self._tmp_dict,key=self._tmp_dict.get, reverse=True):
            yield (k,self._tmp_dict[k])
            #yield (self._position_key_map[k],self._tmp_dict[k])

    def _search(self, search_string, n):
        (self._tfidf, self._index, self._dictionary) = self._subengines[n]
        bag = self.make_bag(search_string,n=n)
        vector = self._wordlist_to_tokens_vector(bag)
        sims = self._index[self._tfidf[vector]]
        matches=dict(enumerate(sims))
        # sorted
        smatches = sorted(matches,key=matches.get)
        for id in smatches:
            key_id = self._position_key_map[id]
            if matches[id]==0:
                continue
            if id in self._tmp_dict:
                self._tmp_dict[key_id]+=matches[id]
            else:
                self._tmp_dict[key_id] = matches[id]

    def prepare(self):
        for i in range(1, TfidfEngine.MAX_NGRAM+1):
            self._prepare(ngram=i)
            self._subengines[i] = (self._tfidf, self._index, self._dictionary)

    def _prepare(self,ngram=1):
        texts = [[word for word in self.make_bag(document, n=ngram)] for document in self._documents.values()]
        frequency = defaultdict(int)

        for text in texts:
            for token in text:
                frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 0]
                  for text in texts]
        dictionary = corpora.Dictionary(texts)
        vectorized = []
        self._position_key_map = {}
        for key, doc in self._documents.items():
            vectorized.append(dictionary.doc2bow(self.make_bag(doc, n=ngram)))
            self._position_key_map[len(vectorized)-1] = key
            
        self._tfidf = models.TfidfModel(vectorized)
        self._index = similarities.SparseMatrixSimilarity(self._tfidf[vectorized], num_features=len(dictionary.keys()))
        self._dictionary = dictionary

    def _wordlist_to_tokens_vector(self, wordlist):
        ''' converts list of words (or ngrams) into 
            attributes (ids) vector 
        '''
        vec = []
        for word in wordlist:
            try:
                vec.append((self._dictionary.token2id[word], 1))
            except KeyError as e:
                # find nearest neighbour (shortest Levenshtein distance) if word doesn't exist
                matches = self._nearest_neighbours(word)
#                print (len(matches))
#                print (matches)
                if len(matches)==0 or matches[0]==None:
                    continue
                for bb in matches:
                    # add weight inversely proportional to number of matches with equal distance
                    vec.append((bb, 1.0/len(matches)))
                print (len(matches))
        return vec

    def _nearest_neighbours(self, word):
        ''' performs nearest neighbour search 
            up to MAX_LEVENSHTEIN_DISTANCE
            returns list of words with same, minimum distance
        '''
        matcher = StringMatcher()
        matcher.set_seq1(word)
        min_dist = (TfidfEngine.MAX_LEVENSHTEIN_DISTANCE, [None])
        
        for token, id in self._dictionary.token2id.items():
            matcher.set_seq2(token)
            try:
                if matcher.distance() < min_dist[0]:
                    min_dist = (matcher.distance(), [id])
                elif matcher.distance() == min_dist[0]:
                    min_dist[1].append(id)
            except Exception as e:
                print (e)
                print(matcher._str1, matcher._str2)
                raise(e)
        return min_dist[1]


class BasicTFIDFSearchTestSuite(unittest.TestCase):
    def setUp(self):
        d0 = "one two three"
        d1 = "one four five six"
        d2 = "one six six eight"
        d3 = "one łan łąki bą"
        d4 = "one reallylongword"
        self.engine = TfidfEngine()
        self.engine.add_documents({
                0:d0,
                1:d1,
                2:d2,
                3:d3,
                4:d4
                })
        self.engine.prepare()
        
    def test_word_in_one(self):
        k = self.engine.find_best_match('five')
        self.assertEqual(k,1)

    def test_utf8_support(self):
        k = self.engine.find_best_match('łąki')
        self.assertEqual(k,3)

    def test_single_mistake_correction(self):
        misspelled_word = "realylongword"

        k = self.engine.find_best_match(misspelled_word)
        self.assertEqual(k,4)

    def test_higher_frequency_higher_value(self):
        kv_dict = {}
        for k, v in self.engine.search('six'):
            kv_dict[k] = v
        self.assertTrue( kv_dict[2] > kv_dict[1])

if __name__ == '__main__':
    unittest.main()
