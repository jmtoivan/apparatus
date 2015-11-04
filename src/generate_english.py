#/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

"""
English poetry generation.

.. module:: generate_english
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

def generate(corpus='./poetry/english_poems.txt',
             db='./graphs/small_graph.db',
             theme=''):
    """
    Generates an English poem.

    :param corpus: poetry corpus
    :param db: graph database
    :param theme: theme of the poem
    :return: poem
    """
    # The character used in the graph to separate words from tags.
    separator = '_'
    # The tags used in the graph.
    tag_list = ['NN', 'VB', 'JJ', 'NNP']

    if db.endswith('lsa.db'):
        separator = '\\'
        tag_list = ['n', 'v', 'a']
    
    return generate_poem('en', corpus, db, tag_list, theme,
                         tag_separator=separator, newline='&')

if __name__ == '__main__':
    main()
