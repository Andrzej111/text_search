from StringMatcher import *

class SlidingBag(object):
    def __init__(self):
        self._x=1

    def set_doc(self, file='t1'):
        self._docfile = file

    def set_word(self, word='destructed'):
        self._matcher = StringMatcher()
        self._word = word
        self._matcher.set_seq1(self._word)

    def run(self):
        wlist=[]
        with open(self._docfile) as f:
            for line in f:
                for word in line.split():
                    self._matcher.set_seq2(word)
                    wlist.append(self._matcher.distance())

        print (min(wlist))