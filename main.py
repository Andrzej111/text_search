from StringMatcher import StringMatcher

if __name__ == "__main__":

    ss = StringMatcher()
    ss.set_seqs('poprawiam','pozdrawiam')

    print (ss.distance())