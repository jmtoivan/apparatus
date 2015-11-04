#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
French word form generation using the `Apertium <http://www.apertium.org/>`_-generator.

.. module:: morphg_fr
"""

import subprocess
import re

def main():
    test = [u'^Vous<prn><pro><p2><mf><pl>$',
            u'^qui<rel><mf><sp>$',
            u'raffolez',
            u'^de<pr>+le<det><def><mf><pl>$',
            u'^squelette<n><m><pl>$']
    print(generate_word_form(test))

def generate_word_form(analysed_text):
    """
    Generates word forms according to the given rules and tries to correct the output.

    >>> generate_word_form(u'^son<det><pos><mf><pl>$ ^beau<adj><m><pl>$ \\
    ... ^cheveu<n><m><pl>$ ;')
    u'ses beaux cheveux \\n'

    :param analysed_text: string or list of lemmas and tags in the form
                          ^lemma<tag1><tag2>...$
    :return: generated words in a string
    """
    output = generate(analysed_text)
    new_output = clean_output(output)
    new_output = elide(new_output)
    new_output = merge_determiners(new_output)
    new_output = add_newlines(new_output)
    return new_output

def generate(analysed_text):
    """
    Generates word forms according to the given rules.

    :param analysed_text: string or list of lemmas and tags in the form
                          ^lemma<tag1><tag2>...$
    :return: generated words in a string
    """
    if isinstance(analysed_text, list):
        analysed_text = ' '.join(analysed_text)
    echo = subprocess.Popen(['echo', analysed_text],
                            shell=False,
                            stdout=subprocess.PIPE)
    morphg = subprocess.Popen\
             (['lt-proc', '-g',
               '/usr/share/apertium/apertium-fr-es/es-fr.autogen.bin'],
              shell=False,
              stdin=echo.stdout,
              stdout=subprocess.PIPE)
    output = morphg.communicate()[0]
    output = unicode(output, 'utf-8')
    return output

def clean_output(output):
    """
    Removes the characters that the generator adds.

    >>> clean_output(u'~ses #beaux ~cheveux ! ;')
    u'ses beaux cheveux ! ;'
    
    :param output: string
    :return: string
    """
    output = output.replace('#', '')
    output = output.replace('*', '')
    output = output.replace('~', '')
    return output

def elide(poem):
    """
    Takes care of the elision.

    >>> elide(u'je ne ai pas de eau')
    u"je n'ai pas d'eau"

    :param poem: the generated poem
    :return: the generated poem with some vowels elided.
    """
    poem_list = poem.split()
    new_poem = []
    i = 0
    words = [u'le', u'la', u'de', u'que', u'je', u'ne', u'se', u'me', u'te']
    vowels = u'aeiouyàáâèéêëîïôùühAEIOUYÀÁÈÉÊH'
    while i < len(poem_list)-1:
        if poem_list[i].lower() in words:
            if poem_list[i+1][0] in vowels:
                short = poem_list[i][:len(poem_list[i])-1] + u'\''
                new_poem.append(short + poem_list[i+1])
                i = i+1
            else:
                new_poem.append(poem_list[i])
        else:
            new_poem.append(poem_list[i])
        i = i+1
    if i < len(poem_list):
        new_poem.append(poem_list[i])
    return ' '.join(new_poem)

def merge_determiners(poem):
    """
    Merges the portmanteau words.

    >>> merge_determiners(u'de les chats')
    u'des chats'

    :param poem: the generated poem
    :return: the generated poem with the portmanteau words merged
    """
    poem_list = poem.split()
    new_poem = []
    i = 0
    mergeables = [(u'À', u'le', u'Au'),
                  (u'à', u'le', u'au'),
                  (u'À', u'les', u'Aux'),
                  (u'à', u'les', u'aux'),
                  (u'De', u'le', u'Du'),
                  (u'de', u'le', u'du'),
                  (u'De', u'les', u'Des'),
                  (u'de', u'les', u'des'),
                  (u'Si', u'il', u'S\'il'),
                  (u'si', u'il', u's\'il'),
                  (u'Si', u'ils', u'S\'ils'),
                  (u'si', u'ils', u's\'ils')]
    while i < len(poem_list)-1:
        added = False
        for m in mergeables:
            if poem_list[i] == m[0] and poem_list[i+1] == m[1]:
                new_poem.append(m[2])
                i = i+1
                added = True
                break
        if not added:
            new_poem.append(poem_list[i])
        i = i+1
    if i < len(poem_list):
        new_poem.append(poem_list[i])
    return ' '.join(new_poem)

def add_newlines(output):
    """
    Puts the newlines and punctuation into the right places.

    >>> add_newlines(u'ses beaux cheveux ! ;')
    u'ses beaux cheveux! \\n'

    :param output: string
    :return: string
    """
    newline_char = ';'
    output = output.replace(newline_char + ' ', '\n')
    output = output.replace(newline_char, '\n')
    output = re.sub(ur' ([\.,\!\?:\'])', '\g<1>', output)
    return output

if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()

