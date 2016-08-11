from io import open
import sys
from DocumentSearcher import DocumentSearcher,TfidfEngine

if __name__ == "__main__":
    documents=[]
    with open('mpc_dump',encoding="utf8") as f:
        for record in f:
            documents.append(record.strip())
    doc_searcher = DocumentSearcher()
    with doc_searcher as searcher:
        searcher.set_documents(documents)
        for k,v in searcher.search(sys.argv[1]):
            print (k,v,searcher.get_document(k))

#    tfidf = TfidfEngine()
#    tfidf.set_stop_regexes(["\d+","de"])
#    print (tfidf.make_bag('de do do 13 da da'))
