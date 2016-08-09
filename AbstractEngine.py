from abc import ABCMeta,abstractmethod
from collections import deque
import re, string
class AbstractSearchEngine(object):
    """abstract class for search engines
    basic usage:
    engine = SomeEngine()
    engine.add_documents(document_list)
    for id,similiarity_value in engine.search('string'):
        
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        # list of strings
        super(AbstractSearchEngine, self).__init__()
        self._documents = {}

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
        ''' supports:
                - dictionaries 
                - lists (keys sequence from 0)
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
#            print('documents: ',self._documents)

    def window(self, seq, n=1):
        it = iter(seq)
        win = deque((next(it, None) for _ in range(n)), maxlen=n)
        yield win
        append = win.append
        for e in it:
            append(e)
            yield win

    # makes bag of printable ngrams
    def make_bag(self, st, n=1):
        bag = []
        for win in self.window(re.sub(r'\W+', ' ', st.lower()).split(), n=n):
            try:
                phrase = ' '.join(list(win))
                bag.append(phrase)
            except TypeError:
                bag.append(win[0])

        return bag



