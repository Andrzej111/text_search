from io import open
import sys
from DocumentSearcher import DocumentSearcher

if __name__ == "__main__":
    documents=[]
    with open('mpc_dump',encoding="utf8") as f:
        for record in f:
            documents.append(record.strip())
    doc_searcher = DocumentSearcher()
    with doc_searcher as searcher:
        searcher.set_documents(documents)
        print (searcher.get_best_match(sys.argv[1]))
