#/usr/env/bin/python
# -*- coding: utf-8 -*-
import re
import morpha_fi
import generate_poem
import tag_fi

def main():

    graph = './graphs/verkko.db'
    text = u"Porsas kiiruhti kissan kanssa kotiin."
    tag_list = ['POS=NOUN','POS=VERB']
    tagged = tag_fi.pos_tag(text)
    substitutes = generate_poem.theme_based_words(u'koira', graph, 7)[0]
    replaced = generate_poem.replace_all('fi', tagged, substitutes, tag_list, '', '_')
    morph = add_morph(tagged, replaced)
    print morph

def add_morph(orig, new):
    orig_poem = u''
    for a, b in orig:
        orig_poem = orig_poem+' '+unicode(a)
    orig_poem = orig_poem.strip()
    new_words  = u''
    for l in new:
        for elem in l:
            el = unicode(elem[0])
            new_words = new_words+' '+el
    new_words = new_words.strip()
    ana_orig = morpha_fi.analyse_morphologically(orig_poem) 
    ana_new = morpha_fi.analyse_morphologically(new_words) 
    orig_wa = morpha_fi.words_with_analyses(ana_orig) 
    new_wa = morpha_fi.words_with_analyses(ana_new)
    mor = morphology(orig, orig_wa, new, new_wa)
    #TO BE FIXED:
    return (mor, [])

#original_poem is a list of tuples containing 
#original words with their pos tags.
#new_poem is a list of tuples containing
#substitute words with their pos tags.
def morphology(original_poem, orig_with_analyses, new_poem, new_with_analyses):
    new_analyses = []
    for i in range(0,len(original_poem)):
        l = []
        for j in range(0,len(new_poem)):
            for word in new_poem[j]:
                if original_poem[i][1] == word[1]:
                    origa = orig_with_analyses[i][1] 
                    newa = new_with_analyses[j][1]
                    modified = modify_analysis(origa, newa)
                    #print 'ORIG: '+origa
                    #print
                    #print 'NEW: '+newa
                    #print
                    #print 'MODIFIED: '+modified
                    #print
                    #print
                    l.append(modified)
        new_analyses.append(l)
    return new_analyses

def modify_analysis(target_form, modifiable_form):
    lemma = get_lemma(modifiable_form)
    ktn = get_ktn(modifiable_form)
    target_form = re.sub(ur"LEMMA=[A-ZÄÖa-zäö0-9']*",
                         "LEMMA='"+lemma+"'", target_form)
    target_form = re.sub(ur'KTN=[0-9]*', ktn, target_form)
    return target_form

def get_num_tag(analysis_string):
    m = re.search(u'NUM=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis_string)
    if not m:
        return ''
    else:
        return m.group(0)

def get_case_tag(analysis_string):
    m = re.findall(u'CASE=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis_string)
    if 'BOUNDARY=COMPOUND' in analysis_string and len(m) > 1:
        return m[-1]
    elif len(m) > 1:
        return m[0]
    else:
        m = re.search(u'CASE=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis_string)
    if not m:
        return ''
    else:
        return m.group(0)

def get_voice_tag(analysis_string):
    m = re.search(u'VOICE=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis_string)
    if not m:
        return ''
    else:
        return m.group(0)

def get_person_tag(analysis_string):
    m = re.search(u'PRS=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ123]*', analysis_string)
    if not m:
        return ''
    else:
        return m.group(0)

def get_allo_tag(analysis_string):
    m = re.search(u'ALLO=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis_string)
    if m == None:
        return ''
    else:
        return m.group(0)

def get_lemma(analysis_string):
    m = re.search(u'LEMMA=[a-zäöåA-ZÄÖÅ\'.,:;!?]*', analysis_string)
    if not m:
        return ''
    else:
        m = re.sub(ur'[\']', '', m.group(0))
        m = m.replace('LEMMA=', '')
        return m

def get_inf_tag(analysis_string):
    m = re.search(u'INF=[ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ]*', analysis_string)
    if not m:
        return ''
    else:
        return m.group(0)  

def get_ktn(analysis_string):  
    m = re.search(u'KTN=[1234567890]*', analysis_string)
    if not m:
        return ''
    else:
        return m.group(0)  

if __name__ == '__main__':
    main()
