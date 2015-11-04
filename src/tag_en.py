#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Part-of-speech tagging of English for poetry generation.

This module uses the following third party tools:

* `Apertium shallow-transfer machine translation engine and
  Apertium linguistic data to translate between English and Spanish
  <http://www.apertium.org/>`_
* `Stanford POS-tagger <http://nlp.stanford.edu/software/tagger.shtml>`_

.. module:: tag
"""

import sys
import os
import re
import subprocess
import tag_en
import helpers

def main():
    test = 'The darkness rolls upward. \
The thick darkness carries with it \
Rain and a ravel of cloud. \
The sun comes forth upon earth.'
    print(pos_tag(test))

def pos_tag(text, tagger='pos_tag_stanford'):
    """
    Part-of-speech tagging. Use this to tag poems.

    >>> pos_tag('O Helen fair! O Helen chaste!\\n\\
    ... If I were with thee, I were blest.')
    [('O', 'UH'), ('Helen', 'NNP'), ('fair', 'JJ'), ('!', '.'), \
('O', 'UH'), ('Helen', 'NNP'), ('chaste', 'JJ'), ('!', '.'), \
('&', 'CC'), ('If', 'IN'), ('I', 'PRP'), ('were', 'VBDR'), \
('with', 'IN'), ('thee', 'PRP'), (',', ','), ('I', 'PRP'), \
('were', 'VBDR'), ('blest', 'VB'), ('.', '.')]
    
    :param text: string of raw text
    :param tagger: the method to use for tagging
    :return: list of analysed words as word-tag tuples ('word', 'tag')
    """
    cleaned = preprocess(text)
    quick_tag = getattr(tag_en, tagger)
    tagged = quick_tag(cleaned)
    
    # Use the apertium tagger to check the tagging.
    try:
        apertium_tags = pos_tag_apertium(cleaned)
        tagged = check_tagging(tagged, apertium_tags)
    # Skip if the apertium tagger is not installed.
    except OSError:
        pass
        
    return tagged

def quick_pos_tag(text, tagger='pos_tag_stanford'):
    """
    Part-of-speech tagging. Use this for quick tagging (of e.g. single words).

    >>> quick_pos_tag(['cat', 'swim', 'sunny'])
    [('cat', 'NN'), ('swim', 'VB'), ('sunny', 'JJ')]
    
    :param text: string or list of text
    :param tagger: the method to use for tagging
    :return: list of analysed words as word-tag tuples ('word', 'tag')
    """
    quick_tag = getattr(tag_en, tagger)
    return quick_tag(text)

def pos_tag_stanford(text, input_file='temp.txt'):
    """
    Part-of-speech tagging using the Stanford tagger.

    >>> pos_tag_stanford('O Helen fair! O Helen chaste!\\n\\
    ... If I were with thee, I were blest.')
    [('O', 'UH'), ('Helen', 'NNP'), ('fair', 'JJ'), ('!', '.'), \
('O', 'UH'), ('Helen', 'NNP'), ('chaste', 'JJ'), ('!', '.'), \
('If', 'IN'), ('I', 'PRP'), ('were', 'VBDR'), ('with', 'IN'), \
('thee', 'PRP'), (',', ','), ('I', 'PRP'), ('were', 'VBDR'), \
('blest', 'VB'), ('.', '.')]
    
    :param text: string or list of words
    :param input_file: name of the file that stores the input for the tagger
    :return: list of word-tag tuples
    """
    if isinstance(text, list):
        text = ' '.join(text)
    helpers.write_to_file(text, input_file)
    script = '../apparatus/stanford-postagger.sh'
    model = '../stanford/models/wsj-0-18-left3words-distsim.tagger'
    tagger = subprocess.Popen([script, model, input_file],
                              shell=False,
                              stdout=subprocess.PIPE)
    output = tagger.communicate()[0]
    output = output.replace('\n', ' ')
    tuples = helpers.strings_to_tuples(output)
    corrected = correct_tags(tuples)
    return corrected

def pos_tag_apertium(text):
    """
    Part-of-speech tagging and morphological analysis using the Apertium tool.

    >>> pos_tag_apertium('the minds')
    [[('the', 'the', '<det><def><sp>')], [('minds', 'mind', '<n><pl>'), \
('minds', 'mind', '<vblex><pri><p3><sg>')]]
    
    :param text: text to tag
    :return: list of lists of token-lemma-tags tuples
    """
    echo = subprocess.Popen(['echo', text],
                            shell=False,
                            stdout=subprocess.PIPE)
    morpha = subprocess.Popen\
             (['lt-proc',
               '/usr/share/apertium/apertium-en-es/en-es.automorf.bin'],
                shell=False,
                stdin=echo.stdout,
                stdout=subprocess.PIPE)
    output = morpha.communicate()[0]
    words = output.split('$')
    tokens = []
    for w in words:
        token = re.search(r'(?<=\^).*?(?=/)', w)
        if token == None:
            token = ''
        else:
            token = token.group(0)
        candidates = re.findall(r'(?<=/).*?(?=/|$)', w)
        if len(candidates) > 0:
            lemma_tag = []
            for c in candidates:
                index = c.find('<')
                if index == -1:
                    lemma = c
                    tag = ''
                else:
                    lemma = c[0:index]
                    tag = c[index:len(c)]
                lemma_tag.append((token, lemma, tag))
            tokens.append(lemma_tag)    
    return tokens

def check_tagging(tagged, apertium_tagged):
    """
    Compares the tags given by two different taggers.

    >>> check_tagging([('O', 'UH'), ('Helen', 'VB'), ('fair', 'JJ')],
    ...               [[('O', '*O', '')],
    ...               [('Helen', 'Helen', '<np><ant><f><sg>')],
    ...               [('fair', 'fair', '<adj><sint>'),
    ...                ('fair', 'fair', '<n><sg>')]])
    [('O', 'UH'), ('Helen', 'TAG'), ('fair', 'JJ')]
    
    :param tagged: list of analysed words as tuples ('word', 'tag')
    :param apertium_tagged: list of lists token-lemma-tags tuples
    :return: list of analysed words as word-tag tuples
    """
    tag_dict = {'NN':'<n>', 'VB':'<vblex>', 'JJ':'<adj>', 'NNP':'<np>'}
    checked = []
    i = 0
    j = 0
    while i < len(tagged):
        if tagged[i][0] != apertium_tagged[j][0][0]:
            if j < len(apertium_tagged)-1:
                j = j+1
        if tagged[i][0] == apertium_tagged[j][0][0]:
            if len(tagged[i]) == 2:
                tag = tagged[i][1]
                if tag_dict.has_key(tag):
                    apertium_tag = tag_dict[tag]
                    if compare_tags(apertium_tagged[j], apertium_tag):
                        checked.append(tagged[i])
                    else:
                        checked.append((tagged[i][0], 'TAG'))
                else:
                    checked.append(tagged[i])
            else:
                checked.append(tagged[i])
        else:
            checked.append(tagged[i])
        i = i+1
        if j < len(apertium_tagged)-1:
            j = j+1
    return checked

def compare_tags(apertium, apertium_tag):
    """
    >>> compare_tags([('Helen', 'Helen', '<np><ant><f><sg>')], '<vblex>')
    False
    """
    if len(apertium) > 0:
        for a in apertium:
            if len(a) == 3:
                if a[2].find(apertium_tag) != -1 or a[2] == '':
                    return True
    return False

def correct_tags(tagged_text):
    """
    Retags some words and changes some tags.

    >>> correct_tags([('thee', 'NN'), ('dogs', 'NNS')])
    [('thee', 'PRP'), ('dogs', 'NN')]
    
    :param tagged_text: list of analysed words as word-tag tuples
    :return: list of analysed words as word-tag tuples
    """
    tag_dict = helpers.read_file_into_dictionary('../apparatus/tags.txt')
    new_text = []
    for token in tagged_text:
        if len(token) < 2:
            continue
        # Changes all the NNS tags (noun plural) to NN (noun singular)
        if token[1] == 'NNS':
            token = (token[0], 'NN')
        # Changes the VBD, VBG, VBN, VBP and VBZ tags to VB
        if token[1].startswith('VB'):
            token = (token[0], 'VB')
        # Retags some specific words defined in the tags.txt file
        if tag_dict.has_key(token[0].lower()):
            token = (token[0], tag_dict[token[0].lower()])
        new_text.append(token)
    return new_text

def preprocess(text):
    """
    Prepares the text for tagging.

    >>> preprocess('O Helen fair! O Helen chaste!\\n\\
    ... If I were with thee, I were blest.')
    'O Helen fair !  O Helen chaste !  & If I were with thee ,  I were blest . '

    :param text: poem or other text
    :return: preprocessed text ready for tagging
    """
    newline_char = '&'
    # Remove parentheses
    text = re.sub(r'[\(\)\[\]]', '', text) 
    text = re.sub(r'([^a-zA-Z0-9\s\-\'])', ' \g<1> ', text)
    # Replace two lines with a white space for not to confuse the analyser.
    text = text.replace('--', ' ')
    # Remove the character that will serve as newline.
    text = text.replace(newline_char, '')
    # The analyser removes the newlines. Replace them with some other character.
    # See morphg.py to return the newlines.
    text = text.replace('\n', ' '+newline_char+' ')
    return text

if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()


