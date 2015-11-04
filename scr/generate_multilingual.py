#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates poems in different languages.

.. module:: generate_multilingual
"""

import generate_english
import generate_french

def main():
    result = generate('fr')
    for r in result:
        print(r)

def generate(language, corpus='', db='', theme=''):
    """
    Generates a poem in the specified language.

    :param language: language id
    :param corpus: text file
    :param db: graph database
    :param theme: theme of the new poem
    :return: poem
    """
    if language == 'en':
        if corpus == '':
            # Default corpus for English
            corpus = './poetry/english_poems.txt'
        if db == '':
            # Default graph for English
            db = './graphs/small_graph.db'
        return generate_english.generate(corpus, db, theme)
    elif language == 'fr':
        if corpus == '':
            # Default corpus for French
            corpus = './poesie/poesie_francaise.txt'
        if db == '':
            # Default graph for French
            db = './graphs/french_pruned.db'
        return generate_french.generate(corpus, db, theme)
            
if __name__ == '__main__':
    main()   
