from AbstractEngine import AbstractSearchEngine


class NgramMatcher(AbstractSearchEngine):
    ''' Searches document in corpus by best matching ngram in search string''' 
    
    def __init__(self):
        super(NgramMatcher, self).__init__()
    