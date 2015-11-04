#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Morphological analysis for English using the `morpha
<http://www.informatics.sussex.ac.uk/research/groups/nlp/carroll/morph.html>`_-analyser.

.. module:: morpha

"""

import sys
import os
import subprocess
import helpers

def main():
    test = [('The', 'DT'), ('darkness', 'NN'), ('rolls', 'NN'), ('upward', 'RB'), ('.', '.'), ('The', 'DT'), ('thick', 'JJ'), ('darkness', 'NN'), ('carries', 'VB'), ('with', 'IN'), ('it', 'PRP'), ('Rain', 'NN'), ('and', 'CC'), ('a', 'DT'), ('ravel', 'NN'), ('of', 'IN'), ('cloud', 'NN'), ('.', '.'), ('The', 'DT'), ('sun', 'NN'), ('comes', 'VB'), ('forth', 'RB'), ('upon', 'IN'), ('earth', 'NN'), ('.', '.')]
    print(analyse_morphologically(test))

def analyse_morphologically(tagged_text, output='str'):
    """
    Morphological analysis of English using the morpha analyser.

    >>> analyse_morphologically([('O', 'UH'), ('Helen', 'NNP'), \\
    ... ('fair', 'JJ'), ('!', '.'), ('O', 'UH'), ('Helen', 'NNP'), \\
    ... ('chaste', 'JJ'), ('!', '.'), ('&', 'CC'), ('If', 'IN'), \\
    ... ('I', 'PRP'), ('were', 'VBDR'), ('with', 'IN'), ('thee', 'PRP'), \\
    ... (',', ','), ('I', 'PRP'), ('were', 'VBDR'), ('blest', 'VB'), \\
    ... ('.', '.')])
    'O_UH Helen_NNP fair_JJ !_. O_UH Helen_NNP chaste_JJ !_. \
&_CC If_IN I_PRP be+ed_VBDR with_IN thee_PRP ,_, \
I_PRP be+ed_VBDR bless+ed_VB ._. \\n'
    
    :param tagged_text: POS-tagged text with the tags separated by underscore
    :param output: the type of the output
    :return: a string of the form lemma+affix_tag or
             a list of tuples of the form ('lemma+affix', 'tag')
    """
    if isinstance(tagged_text, list):
        tagged_text = helpers.tuples_to_strings(tagged_text)
    path = '../morph/morpha'
    echo = subprocess.Popen(['echo', tagged_text],
                            shell=False,
                            stdout=subprocess.PIPE)
    morpha = subprocess.Popen([path, '-act'],
                              shell=False,
                              stdin=echo.stdout,
                              stdout=subprocess.PIPE)
    result = morpha.communicate()[0]
    if output == 'tuple':
        return helpers.strings_to_tuples(result)
    return result
        
if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
