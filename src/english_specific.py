#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
English specific methods for poetry generation.

.. module:: english_specific
"""

import morpha_en
import helpers

def main():
    pass

def add_morph(original, new):
    """
    Adds the original morphological analysis to the replacing words

    >>> add_morph([('The', 'DET'), ('little', 'JJ'), ('boys', 'NN')],\\
    ... [('The', 'DET'), ('furry', 'JJ'), ('cat', 'NN')])
    ([('The', 'DET'), ('furry', 'JJ'), ('cat+s', 'NN')], \
[('furry', 'JJ'), ('cat', 'NN')])
    
    
    :param original: list of the original words with their
                     POS tags as tuples ('word', 'tag')
    :param new: tuple list of the words of the new poem with their POS tags
    :return: a tuple with a tuple list of the lemmas of the new poem with
             the morphological rules for the word form generation and tags,
             and a tuple list of the words used in the replacement
             with their POS tags
    """
    analysis = []
    new_words = []
    if len(original) == len(new):
        morph_orig = morpha_en.analyse_morphologically(original, output='tuple')
        if len(morph_orig) == len(new):
            for i in range(len(morph_orig)):
                if original[i] != new[i]:
                    new_words.append(new[i])
                    affix = ''
                    orig_word = morph_orig[i][0]
                    index = orig_word.find('+')
                    if index != -1:
                        affix = orig_word[index:len(orig_word)]
                    analysis.append((new[i][0]+affix, new[i][1]))
                else:
                    analysis.append(original[i])
    return (analysis, new_words)

def correct_english(analysed):
    """
    Checks that the determiners are correct and capitalizes the I words.

    >>> correct_english([('i', 'PRP'), ('read', 'VB'), ('an', 'DET'), \\
    ... ('book', 'NN')])
    [('I', 'PRP'), ('read', 'VB'), ('a', 'DT'), ('book', 'NN')]
    
    :param analysed: tuple list of words and tags ('word', 'tag')
    :return: tuple list of words and tags ('word', 'tag')
    """
    corrected = []
    vowels = ('a','e','i','o','u','y','A','E','I','O','U','Y')
    for i in range(len(analysed)):
        if analysed[i][0] == 'a':
            if analysed[i+1][0].startswith(vowels):
                corrected.append(('an', 'DT'))
            else:
                corrected.append(analysed[i])
        elif analysed[i][0] == 'A':
            if analysed[i+1][0].startswith(vowels):
                corrected.append(('An', 'DT'))
            else:
                corrected.append(analysed[i])
        elif analysed[i][0] == 'an':
            if not analysed[i+1][0].startswith(vowels):
                corrected.append(('a', 'DT'))
            else:
                corrected.append(analysed[i])
        elif analysed[i][0] == 'An':
            if not analysed[i+1][0].startswith(vowels):
                corrected.append(('A', 'DT'))
            else:
                corrected.append(analysed[i])
        elif analysed[i][0] == 'i':
            corrected.append(('I', 'PRP'))
        else:
            corrected.append(analysed[i])
    return corrected

if __name__ == '__main__':
    import doctest
    doctest.testmod()
