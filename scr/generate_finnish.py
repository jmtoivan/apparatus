#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Finnish poetry generation.

.. module:: generate_finnish
"""
from generate_poem import generate_poem

def main():
    result = generate()
    for r in result:
        print('')
        print(r)

def generate(corpus='./runoutta/runoutta_aakkosellinen.txt',
             db='./graphs/verkko.db',
             theme=''):
    """
    Generates a Finnish poem.

    :param corpus: poetry corpus
    :param db: graph database
    :param theme: theme of the poem
    :return: poem
    """

    # The character used in the graph to separate words from tags.
    separator = '_'
    # The tags used in the graph.
    tag_list = ['POS=NOUN', 'POS=VERB', 'POS=ADJECTIVE', 'POS=ADVERB']
 
    return generate_poem('fi', corpus, db, tag_list, theme,
                         tag_separator=separator, newline='*')

if __name__ == '__main__':
    main()
