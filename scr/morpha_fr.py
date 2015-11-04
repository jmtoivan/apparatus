#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Morphological analysis for French using the 
`Apertium <http://www.apertium.org/>`_-analyser.

.. module:: morpha_fr
"""

import subprocess
import re
import codecs
import helpers

def main():
    text = u"Non, tu n'as pas quitté mes yeux; \
Et quand mon regard solitaire \
Cessa de te voir sur la terre, \
Soudain je te vis dans les cieux."
    print(analyse_morphologically(text))

def analyse_morphologically(text, output='str'):
    """
    Morphological analysis of French using the Apertium analyser.

    >>> analyse_morphologically(u'ses beaux cheveux')
    u'^ses/son<det><pos><mf><pl>$ ^beaux/bel<adj><m><pl>/beau<adj><m><pl>$ \
^cheveux/cheveu<n><m><pl>$\\n\\n'
    >>> analyse_morphologically(u'ses beaux cheveux', output='list')
    [u'^ses/son<det><pos><mf><pl>$', \
u'^beaux/bel<adj><m><pl>/beau<adj><m><pl>$', u'^cheveux/cheveu<n><m><pl>$']
    
    :param text: string or list of words
    :param output: the type of the output
    :return: string (default) or list of the morphologically analysed words
             in the form ^token/lemma<tags>(/alternative lemma<tags>/...)$
    """
    if isinstance(text, list):
        text = ' '.join(text)
    echo = subprocess.Popen(['echo', text],
                            shell=False,
                            stdout=subprocess.PIPE)
    morpha = subprocess.Popen\
             (['lt-proc',
               '/usr/share/apertium/apertium-fr-es/fr-es.automorf.bin'],
                shell=False,
                stdin=echo.stdout,
                stdout=subprocess.PIPE)
    analysed = morpha.communicate()[0] + '\n'
    analysed = unicode(analysed, 'utf-8')
    if output == 'list':
        return split_tokens(analysed)
    return analysed

def split_tokens(text):
    """
    Generates a list of tokens.

    >>> split_tokens(u'^ses/son<det><pos><mf><pl>$ \\
    ... ^beaux/bel<adj><m><pl>/beau<adj><m><pl>$ ^cheveux/cheveu<n><m><pl>$')
    [u'^ses/son<det><pos><mf><pl>$', \
u'^beaux/bel<adj><m><pl>/beau<adj><m><pl>$', u'^cheveux/cheveu<n><m><pl>$']

    :param text: analysed string
    :return: analysed list
    """
    text = re.sub(ur'\n+', '', text)
    splitted = text.split('$')
    word_list = []
    for s in splitted:
        s = s.strip()
        if s != '':
            word_list.append(s + '$')
    return word_list

if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod()
