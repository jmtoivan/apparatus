#/usr/bin/env/python
# -*- coding: utf-8 -*-

"""
Morphological analysis for Finnish using 'omorfi'

.. module:: morpha

"""
import sys, os
import re
import subprocess

def main():
    
    text = u"Porsas kiiruhti käden kanssa kotiin."
    analysis = analyse_morphologically(text)
    pos = pos_tag(analysis)
    wa = words_with_analyses(analysis)
    for i in pos:
        print i[0], i[1]
    for i in wa:
        print i[0], i[1]
    
def analyse_morphologically(text, output='str'):
    if type(text) == list:
        text = ' '.join(text)
    omor_path = '../omorfi/bin/hfst-proc'
    morph_path = '../omorfi/share/hfst/fi/morphology.omor.hfstol'
    
    morpha = subprocess.Popen([omor_path, morph_path],
                              shell=False,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE)
    result = morpha.communicate(text.encode('utf-8'))[0]
    result = unicode(result, 'utf-8')
    return result

def pos_tag(morphological_analysis):
    result = []
    l = morphological_analysis.split('$ ')
    for i in l:
        word = get_word(i)
        pos = get_pos(i)
        result.append((word, pos))
    return result

def words_with_analyses(morphological_analysis):
    result = []
    l = morphological_analysis.split('$ ')
    for i in l:
        word = get_word(i)
        analysis = get_first_analysis(i)
        result.append((word, analysis))
    return result

def get_word(analysis):
    l = analysis.split('/')
    word = l[0].replace('^','')
    return word
    
def get_pos(analysis):
    m = re.findall(u'POS=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis)
    if '[DRV=STI][POS=ADVERB]' in analysis:
        return 'POS=ADVERB'
    elif len(m) > 1 and 'POS=ADJECTIVE' in m:
        return 'POS=ADJECTIVE'
    else:
        m = re.search(u'POS=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis)
    if not m:
        return ''
    else:
        return m.group(0)

def get_first_analysis(analysis):
    l = analysis.split('/')
    return l[1]

if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
