#/usr/env/bin/python
# -*- coding: utf-8 -*-

"""
Finnish word form generation using 'omorfi'

.. module:: morphg_fi
"""
import os, sys
import re
import subprocess
from slave_process import SlaveProcess, slave_process

def main():
    
    analysis1 = u"[BOUNDARY=LEXITEM][LEMMA='prologi'][POS=NOUN][KTN=5][NUM=SG][CASE=NOM][BOUNDARY=LEXITEM][CASECHANGE=NONE]"
    analysis2 = u"[BOUNDARY=LEXITEM][LEMMA='Tuuli'][POS=NOUN][SUBCAT=PROPER][KTN=5][NUM=SG][CASE=NOM][BOUNDARY=LEXITEM][CASECHANGE=NONE]"
    analysis3 = u"[BOUNDARY=LEXITEM][LEMMA='Tuuli'][POS=NOUN][SUBCAT=PROPER][KTN=5][NUM=SG][CASE=NOM][BOUNDARY=LEXITEM][CASECHANGE=NONE] [BOUNDARY=LEXITEM][LEMMA='tuuli'][POS=NOUN][KTN=26][NUM=SG][CASE=NOM][BOUNDARY=LEXITEM][CASECHANGE=NONE] [BOUNDARY=LEXITEM][LEMMA='ja'][POS=CONJUNCTION][SUBCAT=COORD][BOUNDARY=LEXITEM][CASECHANGE=NONE] [BOUNDARY=LEXITEM][LEMMA='prologi'][POS=NOUN][KTN=5][NUM=SG][CASE=NOM][BOUNDARY=LEXITEM][CASECHANGE=NONE]"
    analyses = [[analysis1], [analysis2, analysis3]]
    r = generate_word_form(analyses)
    print r

def generate_word_form(analyses):
    result = []
    omor_path = '../omorfi/bin/hfst-lookup'
    morph_path = '../omorfi/share/hfst/fi/generation.omor.hfstol'
    with slave_process([omor_path, morph_path]) as p:
        for l in analyses:
            ln = []
            for i in l:
                p.stdin.write(i.encode('utf-8')+'\n')
                p.stdin.flush()
                for j in range(2):
                    r = p.stdout.readline()
                    t = r.split('\t')
                    if len(t)>1:
                        ln.append(t[1])
            result.append(ln)
    return result


if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
