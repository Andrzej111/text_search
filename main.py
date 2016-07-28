from TfidfEngine import TfidfEngine
from functools import wraps

if __name__ == "__main__":
    documents=[]
    with open('mpc_dump',encoding="utf8") as f:
        for record in f:
            documents.append(record.strip())
    engine = TfidfEngine()
    engine.add_documents(documents)
    engine.prepare()
    N=3
    result = engine.search('township rebelion',nmax=N)
    for k,v in result:
        print (k,v,engine.get_document_by_id(k))
