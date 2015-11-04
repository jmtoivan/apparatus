#/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

"""
French poetry generation.

.. module:: generate_french
"""

from generate_poem import generate_poem

def main():
    if len(sys.argv) > 1:
        theme = sys.argv[1]
    else:
        theme = ''
    result = generate(theme=theme)
    for r in result:
        print('')
        print(r)

def generate(corpus='./poesie/poesie_francaise.txt',
             db='./graphs/french_pruned.db',
             theme=''):
    """
    Generates a French poem.

    :param corpus: poetry corpus
    :param db: graph database
    :param theme: theme of the poem
    :return: poem
    """
    # The tags used in the graph.
    tag_list = ['NN', 'NNP', 'VB', 'JJ']
    # The character that separates the word and the tag in the graph
    tag_separator = '_'
    # The character that replaces the newline character in text processing
    newline = ';'
    
    return generate_poem('fr', corpus, db, tag_list, theme,
                         tag_separator, newline)

if __name__ == '__main__':
    main()
