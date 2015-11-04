#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
General poetry generation methods.

.. module:: generate_poem
"""

import english_specific, french_specific
import tag_en, tag_fr, tag_fi
import morphg_en, morphg_fr
import bmgraph.db
import helpers 
import codecs
import sqlite3
import random
import sys

def main():
  
    corpus = './runoutta/runoutta_aakkosellinen.txt'
    graph = './graphs/verkko.db'
    chunk = get_chunk_of_corpus(corpus)
    tag_list = ['POS=NOUN','POS=VERB']
    tagged = tag_fi.pos_tag(chunk)
    substitutes = theme_based_words(u'koira', graph, 7)[0]
    replaced = replace_all('fi', tagged, substitutes, tag_list, '', '_')
    generable = finnish_specific.add_morph(tagged, replaced)
    print generable

def generate_poem(language,
                  corpus,
                  db,
                  tag_list,
                  theme='',
                  tag_separator='_',
                  newline='&'):
    """
    Generates a poem.

    :param language: language id, current options en, fr
    :param corpus: poetry corpus
    :param db: graph database
    :param tag_list: list of POS-tags of the words that should be replaced
    :param theme: theme of the poem
    :param tag_separator: character that separates a word and a tag in the graph
    :param newline: the character that marks the place of the newline character
    :return: poem
    """

    # Minimum proportion of new words in the poem
    min_replaced = 0 % 25
    if language == 'fi':
        min_replaced = 0
    # Function to use to tag English.
    # Options:
    # Stanford tagger (recommended): pos_tag_stanford
    tagger = 'pos_tag_stanford'
    
    # Function to use to tag French.
    # Options:
    # MElt tagger (recommended): pos_tag_melt
    # Stanford tagger (doesn't tag proper nouns): pos_tag_stanford
    tagger_fr = 'pos_tag_melt'
    
    # Error messages to show to the user
    error_message = 'ERROR\n\
Not enough words found around the theme \'%s\'. Try with another theme.' % theme
    error_message2 = 'ERROR\n\
Sorry, something went wrong. Try again!'
    error = ('', '', error_message, [], '')
    error2 = ('', '', error_message2, [], '')

    theme = unicode(theme)

    while True:
        for i in range(5):
            ready = False
            random_theme = False
            if theme == '' or theme.isspace():
                theme = choose_random_theme(db, 1)
                random_theme = True

            # Try to solve the POS of the theme if the user hasn't provided it
            elif theme.find(tag_separator) == -1:
                theme = theme.lower()
                if language == 'en':
                    (token, pos_tag) = tag_en.quick_pos_tag(theme,
                                                         tagger=tagger)[0]
                elif language == 'fr':
                    (token, pos_tag) = tag_fr.quick_pos_tag\
                                       (theme, output='tuple', tagger=tagger_fr)[0]
                    
                # Correspondences for the English LSA graph
                tag_dict = {'NN':'n', 'VB':'v', 'JJ':'a', 'NNP':'n'}
                if tag_separator == '\\' and tag_dict.has_key(pos_tag):
                    theme = token + tag_separator + tag_dict[pos_tag]
                else:
                    theme = token + tag_separator + pos_tag

            sys.stdout.write('Looking for theme words...') 
            try:
                (words, goodness) = theme_based_words(theme, db, 20)
                print(' done.')
            except:
                if random_theme:
                    theme = ''
                    print('\nNot enough theme words found.')
                    continue
                else:
                    return error

            # Try to find a poem with enough replaceable words
            # orig_poem is a string of raw text
            orig_poem = get_chunk_of_corpus(corpus)
            orig_poem = helpers.capitalize_after_dot(orig_poem)
            for j in range(5):
                if language == 'en':
                    tagged = tag_en.pos_tag(orig_poem, tagger=tagger)
                elif language == 'fr':
                    tagged = tag_fr.pos_tag(orig_poem, tagger=tagger_fr)
                elif language == 'fi':
                    tagged = tag_fi.pos_tag(orig_poem)
                tag_counter = 0
                for t in tagged:
                    if t[1] in tag_list:
                        tag_counter = tag_counter + 1
                if float(tag_counter)/float(len(tagged))*100 > min_replaced:
                    break
                else:
                    print('Not enough replaceable words.')

            sys.stdout.write('Replacing words...')        
            try:
                replaced = replace_all(language, tagged, words,
                                       tag_list, tagger, tag_separator)
                ready = True
                print(' done.')
                break
            except Exception:
                if random_theme:
                    theme = ''
                    continue
                else:
                    return error
        if not ready:
            if random_theme:
                return error2
            else:
                return error

        sys.stdout.write('Analysing the new words...')        
        if language == 'en':  
            (analysed, replacing_words) = english_specific.add_morph(tagged,
                                                                     replaced)
        elif language == 'fr':
            (analysed, replacing_words) = french_specific.add_morph(tagged,
                                                                    replaced)
        elif language == 'fi':
            (analysed, replacing_words) = finnish_specific.add_morph(tagged,
                                                                     replaced)
        print(' done.')
        number_of_replaced = len(replacing_words)
        number_of_words = len(analysed)
        if number_of_words == 0:
            percent_replaced = 0
        else:
            percent_replaced=float(number_of_replaced)/float(number_of_words)\
                              *100
        if percent_replaced > min_replaced:
            message = str(round(percent_replaced, 0))\
                      +' percent of the words replaced.'
            break
        else:
            print(percent_replaced)
            print('Not enough words replaced.')
            if random_theme:
                theme = ''

    sys.stdout.write('Generating word forms...')
    if language == 'en':
        analysed = english_specific.correct_english(analysed)
        new_poem = morphg_en.generate_word_form(analysed)
    elif language == 'fr':
        analysed = french_specific.place_adjectives(analysed)
        analysed = french_specific.number_agreement(analysed)
        analysed = french_specific.gender_agreement(analysed)
        new_poem = morphg_fr.generate_word_form(analysed)
    elif language == 'fi':
        analysed = morphg_fi.generate_word_form(analysed)
    print(' done.')
    new_poem = new_poem.rstrip()

    theme = theme.split(tag_separator)[0]

    # Generate metadata.
    generate_metadata(replaced, goodness, 'runo_metadata.txt', newline)
    # Generate php file.
    lines = new_poem.split('\n')
    paragraph = '<p>'
    for line in lines:
        paragraph = paragraph + line + '<br />\n'
    paragraph = paragraph + '</p>'
    f = codecs.open('runo.php', 'w', 'utf-8')
    f.write('<h2>' + theme.capitalize() + '</h2>\n')
    f.write(paragraph)
    f.close()
    
    return (theme, orig_poem, new_poem, replacing_words, message)   

def get_chunk_of_corpus(corpus):
    """
    Returns a randomly selected piece of a poem from a text file.

    :param corpus: text file
    :return: some number of successive lines from the text file
    """
    test = ''
    lines = []
    f = codecs.open(corpus, 'r', 'utf-8')
    
    #Go to the randomly selected line
    random_place = random.randint(1, helpers.file_length(corpus)-10)
    for i in range(random_place):
        f.readline()

    while len(lines) < 3:
        test = f.readline()
        #Go to the beginning of the next verse
        while not test.isspace():
            test = f.readline()
            if test == '':
                break
        while test.isspace():
            test = f.readline()
            if test == '':
                break

        while not test.isspace() and len(lines) < 6:
            lines.append(test.strip())
            test = f.readline()
            if test == '':
                break

        sent_end = ('.', '!', '?', ':', ';')
        if not test.isspace():
            if not lines[-1].endswith(sent_end):
                while not test.isspace() and\
                      not lines[-1].endswith(sent_end):
                    lines.append(test.strip())
                    test = f.readline()
                    if test == '':
                        break
        
    f.close

    # Insert a dot to the end
    punctuation = [',', ':', ';']
    last = lines[-1]
    if last[-1].isalpha():
        last = last + '.'
    elif last[-1] in punctuation:
        last = last[:len(last)-1] + '.'
    lines[-1] = last
        
    string = '\n'.join(lines)
    
    return string

def get_verse_of_corpus(corpus, num_words, num_lines):
    """
    Reads some text from a file and formats it.

    The formatted text has the given number of lines and the given
    number of words per line.

    >>> verse = get_verse_of_corpus('../apparatus/poetry/english_poems.txt', 4, 4)
    >>> len(verse.split()) == 16
    True

    :param corpus: text file
    :param num_words: number of words per line
    :param num_lines: number of lines
    :return: random text with the given number of lines and given number
             of words per line
    """
    f = codecs.open(corpus, 'r', 'utf-8')
    
    #Go to the randomly selected line
    random_place = random.randint(1, helpers.file_length(corpus)-10)
    for i in range(random_place):
        f.readline()

    test = ''
    lines = []
    words = []
    i = 0
    test = f.readline()
    words = test.split()
    while len(lines) < num_lines:
        line = []
        while len(line) < num_words:
            if i == len(words):
                i = 0
                test = f.readline()
                if test == '':
                    break
                words = test.split()
            for j in range(i, len(words)):
                if len(line) < num_words:
                    line.append(words[j])
                    i = i+1
                else:
                    break
        lines.append(line)
        
    f.close

    string = ''
    for line in lines:
        string = string + ' '.join(line) + '\n'
    return string

def get_nodes(db, word):
    """
    Looks for neighbouring words for a given word in a graph.
    
    .. important:: 
       Add description.

    :param db:
    :param word:
    :return:
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    nodes = bmgraph.db.edges(conn, word, print_results = False)
    if nodes == None:
        return None
    else:
        result = parse_nodes(nodes, word)
    if len(result) > 200:
        return result[0:200]
    else:
        return result

def parse_nodes(nodes, word):
    """
    .. important:: 
       Add description.

    :param nodes:
    :param word:
    :return:
    """
    result = set()
    for line in nodes:    
        ln = unicode(line)
        l = ln.split(' ')
        l[0] = l[0].replace('stem_', '')
        l[1] = l[1].replace('stem_', '')
        l[3] = l[3].replace('goodness=','')
        l[0] = l[0].replace('Term_', '')
        l[1] = l[1].replace('Term_', '')
        l[3] = l[3].replace('llr=','')
        if l[0] != word:
            result.add((l[0],l[3]))
        if l[1] != word:
            result.add((l[1],l[3]))
        _result = sorted(list(result), key=lambda node: node[1], reverse=True)
        
    return _result

def theme_based_words(theme, db, min_num_words):
    """
    Looks for words around the given theme.

    .. important:: 
       Add description.

    :param theme:
    :param db:
    :param min_num_words:
    :return:
    """
    words = get_nodes(db, theme)
    if words == None or len(words) == 0:
        return []
    while len(words) < min_num_words: 
        counter = 0
        while True:
            rn = random.choice(list(words))
            if len(rn) > 1:
                rn = rn[0]
            more_words = get_nodes(db, rn)
            if more_words == None or len(more_words) == 0:
                continue
            elif counter == 10:
                break
            else:
                words = words.union(more_words)
                break
    themes = [unicode(theme)]
    goodness = [(unicode(theme), 20.0)]
    for w in words:
        themes.append(w[0])
        goodness.append((w[0], round(float(w[1]), 1)))
    return (themes, goodness)

def replace_all(language,
                analysed_poem,
                theme_words,
                tag_list,
                tagger,
                separator='_'):

    """
    Tries to replace all the words with the given tags.

    >>> replace_all('en', [('little', 'JJ'), ('boys', 'NN')], \\
    ... ['cat_NN', 'sleep_VB', 'furry_JJ'], ['NN', 'JJ'], 'pos_tag_stanford')
    [('furry', 'JJ'), ('cat', 'NN')]

    :param language: language id
    :param analysed_poem: list of analysed words as word-tag tuples
    :param theme_words: list of analysed theme based words as word-tag tuples
    :param tag_list: list of tags 
    :param tagger: method to use for tagging
    :param separator: the character that separates the word and the tag
                      in the word list
    :return: list of word-tag tuples
    """
    if language == 'fi':
        new_words = []
        for w in analysed_poem:
            new_words.append((unicode(w[0]), w[1]))
    else:
        new_words = analysed_poem[:]
    for pos_tag in tag_list:
        new_words = replace_words(language, analysed_poem, new_words,
                                  theme_words, pos_tag, tagger, separator)
        if not new_words:
            raise Exception

    return new_words
        
def replace_words(language, analysed_poem, new_words,
                  theme_words, pos_tag, tagger, separator='_'):

    """
    Tries to replace words of the poem with the theme based words.

    >>> replace_words('en', [('little', 'JJ'), ('boys', 'NN')], \\
    ... [('little', 'JJ'), ('boys', 'NN')], ['cat_NN', 'furry_JJ'], \\
    ... 'JJ', 'pos_tag_stanford')
    [('furry', 'JJ'), ('boys', 'NN')]
    >>> replace_words('en', [('little', 'JJ'), ('boys', 'NN')], \\
    ... [('little', 'JJ'), ('boys', 'NN')], [], 'JJ', 'pos_tag_stanford')
     Not enough JJs found.
    False

    :param language: language id
    :param analysed_poem: list of analysed words as word-tag tuples
    :param new_words: list of the words of the poem with the replacing words
    :param theme_words: list of analysed theme based words as word-tag tuples
    :param pos_tag: replaces the words with this tag
    :param tagger: method to use for tagging
    :param separator: the character that separates the word and the tag
                      in the word list
    :return: list of word-tag tuples
    """
    new_poem = []
    tag_dict = {'NN':'NN', 'VB':'VB', 'JJ':'JJ', 'RB':'RB',
                'NNP':'NNP', 'n':'NN', 'v':'VB', 'a':'JJ',
                'POS=NOUN':'POS=NOUN', 'POS=ADJECTIVE':'POS=ADJECTIVE',
                'POS=VERB':'POS=VERB', 'POS=ADVERB':'POS=ADVERB'} 
    candidates = get_words_with_tag(language, theme_words,
                                    pos_tag, tagger, separator)
    # Make sure there are enough new words for the poem.
    if pos_tag != 'NNP':
        tag_count = 0.1
        for w, t in analysed_poem:
            if pos_tag == t:
                tag_count = tag_count + 1
        if language == 'fi':
            limit = 0.2
        else:
            limit = 0.5
        if (len(candidates)/tag_count) < limit:
            print(' Not enough ' + pos_tag + 's found.')
            return False

    for i in range(len(analysed_poem)):
        word = analysed_poem[i]
        if len(word) > 1:
            if word[1] == tag_dict[pos_tag]:
                if language == 'fi':
                    new_words[i] = candidates
                else:
                    l = len(candidates)
                    if l == 1:
                        random_num = 0
                    elif l < 5:
                        random_num = random.randint(0, l-1)
                    else:
                        random_num = biased(0, l-1)
                    new_word = helpers.keep_upper_case\
                        (word[0], candidates[random_num][0])
                    new_words[i] = (new_word, word[1])
    return new_words

def biased(a, b):
    """
    Selects a number between two numbers putting more weight on smaller numbers.

    >>> biased(0, 10) < 11
    True
    
    :param a: lower bound
    :param b: upper bound
    """
    n1 = random.randint(a,int(b/3))
    n2 = random.randint(a,int(b/2))
    n3 = random.randint(a,b)
    r = random.choice([n1, n2, n3])
    return r

def get_words_with_tag(language, words, pos_tag, tagger, separator='_'):
    """
    Returns the words that are tagged with the given tag.

    >>> get_words_with_tag('en', ['cat', 'little'], 'NN', 'pos_tag_stanford')
    [('cat', 'NN')]
    >>> get_words_with_tag('fr', [(u'jouer_VB'), (u'aimer_VB'), \\
    ... (u'peut-être_RB')], 'VB', 'pos_tag_melt')
    [(u'jouer', u'VB'), (u'aimer', u'VB')]

    :language: language id, currently en or fr
    :param words: list of words, optionally tagged <word>_<tag>
    :param tag: POS-tag
    :param tagger: method to use for tagging
    :param separator: the character that separates the word and the tag
                      in the word list
    :return: list of words of the given part of speech
    """
    selected = []
    if len(words) == 0:
        return selected
    else:
        if words[0].find(separator) == -1:
            if language == 'en':
                tagged = tag_en.quick_pos_tag(words, tagger=tagger)
            if language == 'fr':
                tagged = tag_fr.quick_pos_tag(words, tagger=tagger)
            if language == 'fi':
                tagged = tag_fi.quick_pos_tag(words)
        else:
            tagged = helpers.strings_to_tuples(words, separator)
        tagged = helpers.capitalize_nnp(tagged)
        for token in tagged:
            if len(token) > 1:
                if token[1] == pos_tag:
                    selected.append(token)
        return selected

def choose_random_theme(db, number_of_random_words):
    """
    .. important:: 
       Add description.

    :param db:
    :param number_of_random_words:
    :return:
    """
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    theme = bmgraph.db.sample(conn, number_of_random_words, print_results=False)
    theme = parse_themes(theme)
    if len(theme) == 1:
        return theme[0]
    else:
        return theme

def parse_themes(themes):
    """
    .. important:: 
       Add description.

    :param themes:
    :return:
    """
    result = set()
    for line in themes:
        line_2 = unicode(line)
        l = line_2.split(' ')
        theme = l[2].replace('stem_', '')
        theme = theme.replace('Term_', '')
        result.add(theme)
    return list(result)

def generate_metadata(new_words, goodness, output_file, newline='&',
                      separator='_'):
    """
    Writes the POS and relatedness tags of the poem to a file.
    
    :param new_words: new words of the poem as word-tag tuples
    :param goodness: relatedness value of each new word as a list of tuples
                     ('word_TAG', <value>)
    :param output_file: output file
    :param newline: the character that marks the place of the newline character
    :param separator: the character that is used in the graph to separate
                      the word and the tag
    """
    goodness_dict = dict(goodness)
    f = codecs.open(output_file, 'w', 'utf-8')
    for word in new_words:
        if word[0] == newline:
            f.write('\n')
        else:
            f.write('<' + word[1] + '>')
            word_tag = word[0] + separator + word[1]
            if goodness_dict.has_key(word_tag):
                f.write('<' + unicode(goodness_dict[word_tag]) + '>\\')
            else:
                f.write('\\')
    f.close()

if __name__ == '__main__':
    main()
    import doctest
    #doctest.testmod()
