from TfidfEngine import TfidfEngine
from functools import wraps
from io import open
from threading import Thread,Lock
import sys


class DocumentSearcher(object):
    ''' higher level searcher 
        for easier use in scripts and apps
    '''
    # TODO make it use other Engines
    def __init__(self):
        self._lock = Lock()
#        self._outer_lock = Lock()

        # default engine is TF-IDF
        self._engine = TfidfEngine()

    def _set_documents(self, doc_list):
        with self._lock:
            self._engine.clear_documents()       
            self._engine.add_documents(doc_list)
            self._engine.prepare()

    def _add_documents(self, doc_list):
        with self._lock:
            self._engine.add_documents(doc_list)
            self._engine.prepare()

    def set_documents(self, doc_list):
        t1 = Thread(target=self._set_documents, args=(doc_list,))
        t1.start()

    def add_documents(self, doc_list):
        t1 = Thread(target=self._add_documents, args=(doc_list,))
        t1.start()
        
    def search(self,search_string, *args, **kwargs):
        with self._lock:
            return self._engine.search(search_string,*args,**kwargs)

    def get_best_match(self, search_string):
        ''' returns (id, full_document) 2-tuple of best match'''
        best_value = 0.0
        best_m = None
        # should be first but we will check anyways
        for k,v in self.search(search_string):
            if best_value < v:
                best_value = v
                best_m = k
        if best_m is not None:
            return best_m,self._engine.get_document_by_id(best_m)
        else:
            return None

    def get_document(self, id):
        return self._engine.get_document_by_id(id)

    def __enter__(self):
#        self._outer_lock.acquire()
        return self
        
    def __exit__(self,ex,tx,tb):
        pass
#        self._outer_lock.release()
