#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
French specific methods for poetry generation.

.. module:: french_specific
"""

import re
import morpha_fr
import helpers

def main():
    pass

def add_morph(original, new):
    """
    Adds the original morphological analysis to the replacing words.

    >>> add_morph([(u'les', u'DET'), (u'petites', u'JJ'), (u'filles', u'NN')],\\
    ... [(u'les', u'DET'), (u'mignon', u'JJ'), (u'chat', u'NN')])
    ([u'^le<det><def><mf><pl>$', u'^mignon<adj><f><pl>$', \
u'^chat<n><m><pl>$'], \
[(u'mignon', u'JJ'), (u'chat', u'NN')])
    
    :param original: list of the original words with their POS tags as tuples
    :param new: tuple list of the words of the new poem with their POS tags
    :return: a tuple with a list of the lemmas of the new poem with
             the morphological rules for the word form generation
             ('^word<tag1><tag2>...$'), and
             a tuple list of the words used in the replacement
             with their POS tags
    """
    string_orig = ''
    string_new = ''
    analysis = []
    new_words = []
    if len(original) == len(new):
        for i in range(len(original)):
            string_orig = string_orig + original[i][0] + ' '
            string_new = string_new + new[i][0] + ' '
        morph_orig = morpha_fr.analyse_morphologically(string_orig,
                                                       output='list')
        morph_new = morpha_fr.analyse_morphologically(string_new,
                                                      output='list')

        if len(morph_orig) == len(morph_new):
            for i in range(len(morph_orig)):
                pos = original[i][1]
                block_list = [u'avoir',  #have
                              u'être',   #be
                              u'aller',  #go
                              u'venir',  #come
                              u'faire',  #do
                              u'vouloir']#want
                block = False
                for b in block_list:
                    if morph_orig[i].lower().find(b) != -1:
                        block = True
                if block:
                    new_word = re.sub(ur'\^(.*?)/.*', '\g<1>', morph_orig[i])
                elif morph_orig[i] != morph_new[i]:
                    (new_word, is_new) = find_correct_analysis(morph_new[i],
                                                               morph_orig[i],
                                                               pos)
                    if is_new:
                        new_words.append(new[i])
                else:
                    (new_word, is_new) = find_correct_analysis(morph_orig[i],
                                                               morph_orig[i],
                                                               pos)
                analysis.append(new_word)
    return (analysis, new_words)
                
def find_correct_analysis(new_analysis, orig_analysis, pos_tag):
    """
    Tries to select the correct analysis.

    >>> find_correct_analysis(u'^chat/chat<n><m><sg>$', \\
    ... u'^filles/fils<n><f><pl>/fille<n><f><pl>$', u'NN')
    (u'^chat<n><m><pl>$', True)

    :param new_analysis: the morphological analysis of the new word
    :param orig_analysis: the morphological analysis of the original word
    :param pos_tag: POS-tag of the original word
    :return: a tuple with a word with a single morphological analysis,
             and True if the word is new, False otherwise
    """
    tag_dict = {'NN':'<n>', 'JJ':'<adj>', 'RB':'<adv>', 'NNP':'<np>',
                'VB':'<vblex>', 'DET':'<det>', 'PRO':'<prn>', 'P':'<pr>'}
    if tag_dict.has_key(pos_tag):
        pos = tag_dict[pos_tag]
    else:
        pos = '<[^/]*>'
    morph = re.search(ur'%s([^/]*>)?' %pos, orig_analysis)
    if morph != None:
        if new_analysis.find(pos) != -1:
            new_word = re.sub(ur'.*?/([^/]*?)%s.*' %pos, '\g<1>', new_analysis)
        else:
            new_word = re.sub(ur'\^.*?/\*?(.*?)[<\$].*', '\g<1>', new_analysis)
        correct_analysis = ('^' + new_word + morph.group(0) + '$', True)
    else:
        morph = re.search(ur'(<.*?>)+', orig_analysis)
        orig_word = re.sub(ur'\^.*?/\*?(.*?)[<\$].*', '\g<1>', orig_analysis)
        if morph != None:
            correct_analysis = ('^' + orig_word + morph.group(0) + '$', False)
        else:
            correct_analysis = ('^' + orig_word + '$', False)
    # Keep the original gender of nouns
    if correct_analysis[0].find('<n>') != -1:
        correct_analysis = (keep_gender(correct_analysis[0], new_analysis),
                            correct_analysis[1])
    return correct_analysis

def keep_gender(new_analysis, orig_analysis):
    """
    Keeps the gender of the new word in the new analysis.

    >>> keep_gender(u'^chat<n><f><pl>$', u'^chat/chat<n><m><sg>$')
    u'^chat<n><m><pl>$'

    :param new_analysis: new morphological analysis of the word
    :param orig_analysis: original morphological analysis of the word
    :return: new morhological analysis of the word with the original gender
    """
    if new_analysis.find('<n>') != -1:
        g = find_gender(orig_analysis)
        if g != '':
            g_new = find_gender(new_analysis)
            if g_new != '':
                new_analysis = new_analysis.replace(g_new, g)
    return new_analysis

def gender_agreement(poem_list):
    """
    Takes care of the gender agreement.

    >>> gender_agreement([u'^le<det><def><f><pl>$', u'^petit<adj><f><pl>$', \\
    ... u'^chat<n><m><pl>$', u'^noir<adj><f><pl>$'])
    [u'^le<det><def><m><pl>$', u'^petit<adj><m><pl>$', u'^chat<n><m><pl>$', \
u'^noir<adj><m><pl>$']
    
    :param poem_list: list of the lemmas of the new poem with the morphological
                      rules for the word form generation
                      (['^word<tag1><tag2>...$',...])
    :return: the input list with the corrected gender agreement
    """
    for i in range(1, len(poem_list)):
        if poem_list[i].find('<n>') != -1:
            g = find_gender(poem_list[i])
            if g != '':
                # Look for the preceding adjectives
                j = 1
                while poem_list[i-j].find('<adj>') != -1 and i-j >= 0:
                    g_adj = find_gender(poem_list[i-j])
                    if g_adj != '':
                        poem_list[i-j] = poem_list[i-j].replace(g_adj, g)
                    j = j+1
                # Look for the preceding determiner
                if poem_list[i-j].find('<det>') != -1:
                    g_det = find_gender(poem_list[i-j])
                    if g_det != '':
                        poem_list[i-j] = poem_list[i-j].replace(g_det,g)
                # Look for the following adjectives
                k = 1
                while i+k < len(poem_list):
                    if poem_list[i+k].find('<adj>') != -1:
                        g_adj = find_gender(poem_list[i+k])
                        if g_adj != '':
                            poem_list[i+k] = poem_list[i+k].replace(g_adj, g)
                        k = k+1
                    elif poem_list[i+k].find('<cnjcoo>') != -1:
                        k = k+1
                    else:
                        break
    return poem_list

def find_gender(word):
    """
    Returns the gender tag of the word.

    >>> find_gender(u'^chat/chat<n><m><sg>$')
    '<m>'

    :param word: a morphologically analysed word
    :return: gender tag
    """
    gender = ''
    if word.find('<m>') != -1:
        gender = '<m>'
    elif word.find('<f>') != -1:
        gender = '<f>'
    #elif word.find('<mf>') != -1:
    #    gender = '<mf>'
    return gender

def number_agreement(poem_list):
    """
    Takes care of the number agreement.

    >>> number_agreement([u'^le<det><def><m><pl>$', u'^petit<adj><m><sg>$', \\
    ... u'^chat<n><m><sg>$', u'^noir<adj><m><sg>$'])
    [u'^le<det><def><m><pl>$', u'^petit<adj><m><pl>$', u'^chat<n><m><pl>$', \
u'^noir<adj><m><pl>$']
    
    :param poem_list: list of the lemmas of the new poem with the morphological
                      rules for the word form generation
                      (['^word<tag1><tag2>...$',...])
    :return: the input list with the corrected number agreement
    """
    for i in range(len(poem_list)):
        if poem_list[i].find('<det>') != -1:
            n = find_number(poem_list[i])
            if n != '':
                # Look for the following adjectives
                k = 1
                while i+k < len(poem_list):
                    if poem_list[i+k].find('<adj>') != -1:
                        n_adj = find_number(poem_list[i+k])
                        if n_adj != '':
                            poem_list[i+k] = poem_list[i+k].replace(n_adj, n)
                        k = k+1
                    elif poem_list[i+k].find('<cnjcoo>') != -1:
                        k = k+1
                    else:
                        break
                if i+k < len(poem_list):
                    # Look for the following noun
                    if poem_list[i+k].find('<n>') != -1:
                        n_noun = find_number(poem_list[i+k])
                        if n_noun != '':
                            poem_list[i+k] = poem_list[i+k].replace(n_noun, n)
                        k = k+1
                    if i+k < len(poem_list):
                        # Look for the adjectives following the noun
                        while i+k < len(poem_list):
                            if poem_list[i+k].find('<adj>') != -1:
                                n_adj = find_number(poem_list[i+k])
                                if n_adj != '':
                                    poem_list[i+k] = poem_list[i+k].replace\
                                                     (n_adj, n)
                                k = k+1
                            elif poem_list[i+k].find('<cnjcoo>') != -1:
                                k = k+1
                            else:
                                break
    return poem_list

def find_number(word):
    """
    Returns the number tag of the word.

    >>> find_number(u'^chat/chat<n><m><sg>$')
    '<sg>'

    :param word: a morphologically analysed word
    :return: number tag
    """
    number = ''
    if word.find('<sg>') != -1:
        number = '<sg>'
    elif word.find('<pl>') != -1:
        number = '<pl>'
    elif word.find('<sp>') != -1:
        number = '<sp>'
    return number

def place_adjectives(poem_list):
    """
    Places the adjectives.

    >>> place_adjectives([u'^le<det><def><m><pl>$', u'^noir<adj><m><sg>$', \\
    ... u'^chat<n><m><sg>$'])
    [u'^le<det><def><m><pl>$', u'^chat<n><m><sg>$', u'^noir<adj><m><sg>$']

    :param poem_list: list of the lemmas of the new poem with the morphological
                      rules for the word form generation
                      (['^word<tag1><tag2>...$',...])
    :return: the input list with the corrected adjective placement
    """    
    # The adjectives that are placed before the noun
    adjectives = [u'autre',     #other
                  u'grand',     #big
                  u'joli',      #pretty
                  u'petit',     #little
                  u'beau',      #beautiful
                  u'bel',       
                  u'gros',      #fat
                  u'mauvais',   #bad
                  u'vieux',     #old
                  u'bon',       #good
                  u'jeune',     #young
                  u'nouveau',   #new
                  u'premier',   #first
                  u'deuxième',  #second
                  u'troisième', #third
                  u'seul',      #only
                  u'gentil',    #kind
                  u'méchant',   #mean
                  u'meilleur',  #better
                  u'court',     #short
                  u'moyen']     #middle   
    new_poem = [poem_list[0]]
    for i in range(1, len(poem_list)):
        adj_found = False
        if poem_list[i].find('<n>') != -1:
            if poem_list[i-1].find('<adj>') != -1:
                for a in adjectives:
                    if poem_list[i-1].lower().find(a) != -1:
                        adj_found = True
                        break
                if not adj_found:
                    new_poem.pop()
                    new_poem.append(poem_list[i])
                    new_poem.append(poem_list[i-1])
                else:
                    new_poem.append(poem_list[i])
            else:
                new_poem.append(poem_list[i])
        else:
            new_poem.append(poem_list[i])
    return new_poem
                

if __name__ == '__main__':
    import doctest
    doctest.testmod()
