from StringMatcher import StringMatcher
from SlidingBag import SlidingBag
if __name__ == "__main__":

    ss = StringMatcher()
    ss.set_seqs('poprawiam','pozdrawiam')

    print (ss.distance())

    sb = SlidingBag()
    sb.set_doc('txt_files/t2')
    sb.set_word()
    sb.run()