#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
English word form generation using the `morphg
<http://www.informatics.sussex.ac.uk/research/groups/nlp/carroll/morph.html>`_-generator.

.. module:: morphg
"""

import sys
import os
import subprocess
import re

def main():
    test = [('Shadow','NN'),('and','CC'),('``', '``'),('sunlight','NN'),
            ("''", "''"),('be+','VBR'),('the','DT'),('same','JJ')]
    generated = generate_word_form(test)
    print(generated)

def generate_word_form(word_affix_tag):
    """
    Generates word forms according to the given rules.

    >>> generate_word_form([('O', 'UH'), ('Helen', 'NNP'), ('fair', 'JJ'), \\
    ... ('!', '.'), ('O', 'UH'), ('Helen', 'NNP'), ('chaste', 'JJ'), \\
    ... ('!', '.'), ('&', 'CC'), ('If', 'IN'), ('I', 'PRP'), \\
    ... ('be+ed', 'VBDR'), ('with', 'IN'), ('thee', 'PRP'), (',', ','), \\
    ... ('I', 'PRP'), ('be+ed', 'VBDR'), ('bless+ed', 'VB'), ('.', '.')])
    'O Helen fair! O Helen chaste! \\nIf I were with thee, I were blessed. \\n'
    
    :param word_affix_tag: list of words and tags as tuples
                           ('word+affix', 'POS-tag')
    :return: generated words in a string
    """
    string = ''
    for word in word_affix_tag:
        if len(word) > 1:
            string = string + word[0] + '_' + word[1] + ' '
        else:
            string = string + word[0]
    fullpath = '../morph/morphg'
    echo = subprocess.Popen(['echo', string],
                            shell=False,
                            stdout=subprocess.PIPE)
    morphg = subprocess.Popen([fullpath, '-c'],
                              shell=False,
                              stdin=echo.stdout,
                              stdout=subprocess.PIPE)
    output = morphg.communicate()[0]
    new_output = clean_output(output)
    return new_output

def clean_output(output):
    """
    Puts the newlines and punctuation into the right places.

    >>> clean_output('O Helen fair ! O Helen chaste ! \\
    ... & If I were with thee , I were blessed .')
    'O Helen fair! O Helen chaste! \\nIf I were with thee, I were blessed.'
    
    :param output: string
    :return: string
    """
    newline_char = '&'
    new_output = output.replace(newline_char + ' ', '\n')
    new_output = new_output.replace(newline_char, '\n')
    new_output = re.sub(r' ([.,!?:;\'])', r'\1', new_output)
    new_output = new_output.replace('`` ', '"')
    new_output = new_output.replace('` ', '\'')
    new_output = new_output.replace('\'\'', '\"')
    new_output = new_output.replace('" ', '"')
    return new_output
    
if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()

