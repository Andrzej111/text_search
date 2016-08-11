from abc import ABCMeta,abstractmethod
from collections import deque
import re, string
class AbstractSearchEngine(object):
    """abstract class for search engines
    basic usage:
    engine = SomeEngine()
    engine.add_documents(document_list_or_string)
    engine.prepare()
    for id,similarity_value in engine.search('my favourite string'):
        something
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractSearchEngine, self).__init__()
        self._documents = {}
        self._stop_regexes = []

    @abstractmethod
    def search(self, search_string):
        pass

    @abstractmethod
    def prepare(self):
        pass

    def _next_numeric_id(self):
        iterator = len (self._documents.keys())
        while True:
            if iterator not in self._documents.keys():
                return iterator
            iterator+=1

    def add_documents(self, documents):
        ''' adds documents to corpus
            probably need to run prepare() after, to use engine 
            supports:
                - dictionaries 
                - lists (keys sequence from 0)
            but DO NOT mix both in same engine
        '''
        if isinstance(documents, list):
            for doc in documents:
                self._documents[self._next_numeric_id()]=doc
        elif isinstance(documents, dict):
            self._documents.update(documents)
        else:
            raise TypeError("\"Documents\" can only be dictionary or list")

    def clear_documents(self):
        self._documents = {}

    def get_document_by_id(self, id):
        try:
            return self._documents[id]
        except Exception as e:
            print (e)
            print ('id: ',id)

    def window(self, seq, n=1):
        it = iter(seq)
        win = deque((next(it, None) for _ in range(n)), maxlen=n)
        yield win
        append = win.append
        for e in it:
            append(e)
            yield win

    def set_stop_regexes(self, regex_strings):
        ''' sets regular expressions for which words are exluded from searching 
            example:
                some_engine.set_stop_regexes(['\d+','the'])
        ''' 
        self._stop_regexes = list(regex_strings)
                
    def string_matches_any(self, string, regexes):
        for r in regexes:
            if re.match(r,string):
                return True
        return False

    def make_bag(self, st, n=1):
        ''' makes bag of printable ngrams
            after splitting words removes these that match any of self._stop_regexes'''
        bag = []
        sequence = re.sub(r'\W+', ' ', st.lower()).split()
        sss = []
        for seq_i in sequence:
            if not self.string_matches_any(seq_i, self._stop_regexes):
                sss.append(seq_i)
        for win in self.window(sss, n=n):
            try:
                phrase = ' '.join(list(win))
                bag.append(phrase)
            except TypeError:
                bag.append(win[0])

        return bag



