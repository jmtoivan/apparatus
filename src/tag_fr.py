#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Part-of-speech tagging of French for poetry generation.

This module uses the following third party tools:

* `MElt POS-tagger
  <http://raweb.inria.fr/rapportsactivite/RA2009/alpage/uid89.html>`_
* `Apertium shallow-transfer machine translation engine and
  Apertium linguistic data to translate between French and Spanish
  <http://www.apertium.org/>`_
* `Stanford POS-tagger <http://nlp.stanford.edu/software/tagger.shtml>`_

.. module:: tag_fr
"""

import sys
import os
import subprocess
import re
import codecs
import tag_fr
import morpha_fr
import helpers

def main():
    text = u"Non, tu n'as pas quitté mes yeux; \
Et quand mon regard solitaire \
Cessa de te voir sur la terre, \
Soudain je te vis dans les cieux."
    print(pos_tag(text))

def pos_tag(text, output='tuple', tagger='pos_tag_melt'):
    """
    Part-of-speech tagging. Use this to tag poems.

    >>> pos_tag(u'ses beaux cheveux')
    [(u'ses', u'DET'), (u'beaux', u'JJ'), (u'cheveux', u'NN')]
    >>> pos_tag(u'ses beaux cheveux', output='str')
    u'ses_DET beaux_JJ cheveux_NN '

    :param text: string of raw text
    :param tagger: the method to use for tagging
    :return: list of analysed words as word-tag tuples (default),
             or string with an underscore separating the word and the tag
    """
    preprocessed = preprocess(text)
    tagged_list = tag_with_apertium(preprocessed, tagger)
    tuples = []
    for item in tagged_list:
        tupl_list = helpers.strings_to_tuples(item)
        if len(tupl_list) == 1:
            if tupl_list[0][0] != '':
                tuples.append(tupl_list[0])
        elif len(tupl_list) > 1:
            words = ''
            for i in range(len(tupl_list)-1):
                words = words + tupl_list[i][0] + ' '
            words = words + tupl_list[-1][0]
            tuples.append((words, tupl_list[-1][1]))
    if output == 'str':
        return helpers.tuples_to_strings(tuples)
    return tuples

def quick_pos_tag(text, output='tuple', tagger='pos_tag_melt'):
    """
    Part-of-speech tagging. Use this for quick tagging (of e.g. single words).

    >>> quick_pos_tag([u'chat', u'aimer'])
    [(u'chat', u'NN'), (u'aimer', u'VB')]

    :param text: string of raw text
    :param tagger: the method to use for tagging
    :return: list of analysed words as word-tag tuples (default),
             or string with the underscore separating the word and the tag 
    """
    tag = getattr(tag_fr, tagger)
    if output=='str':
        try:
            tagged = tag(text, output='str')
        # Use the Stanford tagger if MElt is not installed.
        except OSError:
            tagged = pos_tag_stanford(text, output='str')
    else:
        try:
            tagged = tag(text, output='tuple')
        except OSError:
            tagged = pos_tag_stanford(text, output='tuple')
    return tagged

def tag_with_apertium(text, tagger='pos_tag_melt'):
    """
    Uses Apertium to tokenize the words and tagger to tag the tokens.

    >>> tag_with_apertium(u'ses beaux cheveux')
    [u'ses_DET', u'beaux_JJ', u'cheveux_NN']

    :param text: string of words
    :param tagger: method to use for POS-tagging
    :return: list of tagged words with an underscore separating
             the word and the tag
    """
    analysed = morpha_fr.analyse_morphologically(text, output='list')
    string = ''
    for a in analysed:
        word = re.sub(ur'\^(.*?)/.*', '\g<1>', a)
        string = string + word + ' $ '
    # Use the function given in the tagger variable
    tag = getattr(tag_fr, tagger)
    try:
        tagged = tag(string)
    # Use the Stanford tagger if MElt is not installed.
    except OSError:
        tagged = pos_tag_stanford(string)
    tagged = re.sub(ur'\$_.*? ', '$ ', tagged)
    words = tagged.split('$')
    trimmed = []
    for w in words:
        w = w.strip()
        if w != '':
            trimmed.append(w)
    return trimmed

def pos_tag_melt(text, output='str', input_file='temp.txt'):
    """
    Part-of-speech tagging using the MElt tagger.

    >>> pos_tag_melt(u'ses beaux cheveux')
    u'ses_DET beaux_JJ cheveux_NN '
    >>> pos_tag_melt(u'ses beaux cheveux', output='list')
    [u'ses_DET', u'beaux_JJ', u'cheveux_NN']
    >>> pos_tag_melt(u'ses beaux cheveux', output='tuple')
    [(u'ses', u'DET'), (u'beaux', u'JJ'), (u'cheveux', u'NN')]

    :param text: string or list of words
    :param output: the output format
    :param input_file: name of the file that stores the input for the tagger
    :return: string (default) with an underscore separating
             the word and the tag, list , or list of word-tag tuples
    """
    if isinstance(text, list):
        text = ' '.join(text)
    helpers.write_to_file(text, input_file)
    cat = subprocess.Popen(['cat', input_file],
                            shell=False,
                            stdout=subprocess.PIPE)
    melt = subprocess.Popen\
             (['MElt'],
              shell=False,
              stdin=cat.stdout,
              stdout=subprocess.PIPE)
    tagged = melt.communicate()[0]
    tagged = unicode(tagged, 'utf-8')
    tuples = helpers.strings_to_tuples(tagged, '/')
    tuples = correct_tags_melt(tuples)
    if output == 'list':
        return helpers.tuples_to_strings(tuples, output='list')
    if output == 'tuple':
        return tuples
    return helpers.tuples_to_strings(tuples, output='str')

def pos_tag_stanford(text, output='str', input_file='temp.txt'):
    """
    Part-of-speech tagging using the Stanford tagger.

    >>> pos_tag_stanford(u'ses beaux cheveux')
    u'ses_D beaux_JJ cheveux_NN '
    >>> pos_tag_stanford(u'ses beaux cheveux', output='list')
    [u'ses_D', u'beaux_JJ', u'cheveux_NN']
    >>> pos_tag_stanford(u'ses beaux cheveux', output='tuple')
    [(u'ses', u'D'), (u'beaux', u'JJ'), (u'cheveux', u'NN')]
    
    :param text: string or list of words
    :param output: the output format
    :param input_file: name of the file that stores the input for the tagger
    :return: string (default) with an underscore separating
             the word and the tag, list , or list of word-tag tuples
    """
    if isinstance(text, list):
        text = ' '.join(text)
    helpers.write_to_file(text, input_file)
    script = '../apparatus/stanford-postagger.sh'
    model = '../stanford/models/french.tagger'
    tagger = subprocess.Popen([script, model, input_file],
                              shell=False,
                              stdout=subprocess.PIPE)
    tagged = tagger.communicate()[0]
    tagged = unicode(tagged, 'utf-8')
    tagged = tagged.replace('\n', ' ')
    tuples = helpers.strings_to_tuples(tagged, '_')
    tuples = correct_tags_stanford(tuples)
    if output == 'list':
        return helpers.tuples_to_strings(tuples, output='list')
    if output == 'tuple':
        return tuples
    return helpers.tuples_to_strings(tuples, output='str')

def correct_tags_melt(tagged_text):
    """
    Changes some tags of the Stanford tagger.

    >>> correct_tags_melt([(u'ses', u'DET'), (u'beaux', u'ADJ'), \\
    ... (u'cheveux', u'NC')])
    [(u'ses', u'DET'), (u'beaux', u'JJ'), (u'cheveux', u'NN')]
    
    :param tagged_text: list of analysed words as word-tag tuples
    :return: list of analysed words as word-tag tuples
    """
    new_text = []
    tag_dict = {u'NC':u'NN', u'ADJ':u'JJ', u'ADV':u'RB', u'NPP':u'NNP'}
    for token in tagged_text:
        if len(token) < 2:
            continue
        # Always analyse the word 'tu' as CLS
        if token[0] == u'tu' or token[0] == u'Tu':
            token = (token[0], u'CLS')
        if token[1].startswith(u'V'):
            token = (token[0], u'VB')
        if tag_dict.has_key(token[1]):
            token = (token[0], tag_dict[token[1]])
        new_text.append(token)
    return new_text

def correct_tags_stanford(tagged_text):
    """
    Changes some tags of the Stanford tagger.

    >>> correct_tags_stanford([(u'ses', u'D'), (u'beaux', u'A'), \\
    ... (u'cheveux', u'N')])
    [(u'ses', u'D'), (u'beaux', u'JJ'), (u'cheveux', u'NN')]

    :param tagged_text: list of analysed words as word-tag tuples
    :return: list of analysed words as word-tag tuples with the systems
             default POS-tags 
    """
    new_text = []
    for token in tagged_text:
        if len(token) < 2:
            continue
        if token[1] == u'N':
            token = (token[0], u'NN')
        if token[1].startswith(u'A'):
            token = (token[0], u'JJ')
        if token[1].startswith(u'V'):
            token = (token[0], u'VB')
        new_text.append(token)
    return new_text

def preprocess(corpus):
    """
    Prepares the text for tagging.

    >>> preprocess(u'Un poète pieux, ennemi du sommeil,') ==\\
    ... u'Un poète pieux , ennemi de le sommeil ,'
    True
    
    :param text: poem or other text
    :return: preprocessed text ready for tagging
    """    
    newline_char = ';'   
    # Eliminate the character that will serve as newline.
    corpus = corpus.replace(newline_char, ',')
    # The analyser removes the newlines. Replace them with some other character.
    # See morphg_fr.py to return the newlines.
    corpus = corpus.replace('\n', ' '+newline_char+' ')

    # Remove parentheses
    corpus = re.sub(r'[\(\)\[\]]', '', corpus)
    # Add spaces before punctuation marks
    corpus = re.sub(ur'(?<!M)\.', ' .', corpus)
    corpus = corpus.replace(',', ' ,')
    corpus = corpus.replace('?', ' ?')
    corpus = corpus.replace('!', ' !')
    corpus = corpus.replace(':', ' :')
    corpus = corpus.replace(' - ', ' ')
    corpus = corpus.replace('--', ' ')
    #corpus = re.sub(ur'[\(\)_,\"\*@=#&{}<>/\$%\[\]~\+;:"«»,]', '', corpus)

    # Divide preposition+determiner portmanteaus
    corpus = corpus.replace(u' au ', u' à le ')
    corpus = corpus.replace(u'Au ', u'À le ')
    corpus = corpus.replace(u' aux ', u' à les ')
    corpus = corpus.replace(u'Aux ', u'À les ')
    corpus = corpus.replace(u' du ', u' de le ')
    corpus = corpus.replace(u'Du ', u'De le ')
    corpus = corpus.replace(u' des ', u' de les ')
    corpus = corpus.replace(u'Des ', u'De les ')
    return corpus

if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
