#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Some useful methods to use with poetry generation.

.. module:: helpers
"""

import codecs

def write_to_file(text, output_file):
    """
    Writes the given string or list to the given file.

    :param text: string or list of strings
    :param output_file: name of the output file
    """
    f = codecs.open(output_file, 'w', 'utf-8')
    if isinstance(text, list):
        for t in text:
            f.write(t)
    else:
        f.write(text)
    f.close()

def read_file_into_dictionary(file_name):
    """
    Reads a text file and converts it into a dictionary.
    
    :param file_name: text file with a key and a word in one line
                      separated by a whitespace
    :return: python dictionary
    """
    f = open(file_name)
    text = f.read()
    f.close()
    line_list = text.split('\n')
    d = {}
    for line in line_list:
        splitted = line.split()
        if len(splitted) == 2:
            d[splitted[0]] = splitted[1]
    return d

def tuples_to_strings(tagged, separator='_', output='str'):
    """
    Converts tuples to strings.

    >>> tuples_to_strings([('cat', 'NN'), ('dog', 'NN')])
    'cat_NN dog_NN '
    >>> tuples_to_strings([('cat', 'NN'), ('dog', 'NN')], output='list')
    ['cat_NN', 'dog_NN']
    >>> tuples_to_strings(('cat', 'NN'), separator='/')
    'cat/NN'
    
    :param tagged: list of tuples (<word>, <tag>) or tuple 
    :param separator: the separating character e.g. '_'
    :return: <word><separator><tag> string or list
    """
    if isinstance(tagged, list):
        if output == 'str':
            processed = ''
            for token in tagged:
                processed = processed + token[0] + separator + token[1] + ' '
            return processed
        elif output == 'list':
            processed = []
            for token in tagged:
                processed.append(token[0] + separator + token[1])
            return processed
    elif isinstance(tagged, tuple):
        return tagged[0] + separator + tagged[1]

def strings_to_tuples(analysed, separator='_'):
    """
    Converts a string or a list to a list of tuples.

    >>> strings_to_tuples('cat_NN dog_NN ')
    [('cat', 'NN'), ('dog', 'NN')]
    >>> strings_to_tuples(['cat_NN', 'dog_NN'])
    [('cat', 'NN'), ('dog', 'NN')]
    >>> strings_to_tuples('cat/NN', '/')
    [('cat', 'NN')]

    :param analysed: string or list of analysed words in the form
                     <word><separator><tag>
    :param separator: the separating character e.g. '_'
    :return: list of tuples (<word>, <tag>)
    """
    tuple_list = []
    if isinstance(analysed, basestring):
        tokens = analysed.split()
    else:
        tokens = analysed
    for token in tokens:
        word_tag = token.split(separator)
        tuple_list.append(tuple(word_tag))
    return tuple_list

def file_length(file_name):
    """
    Counts the rows of the file.

    .. important:: 
       Add description.

    :param file_name:
    :return:
    """
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def keep_upper_case(old_word, new_word):
    """
    Given two words, capitalizes the second if the first is capitalized.

    >>> keep_upper_case('Donald', 'mickey')
    'Mickey'
    >>> keep_upper_case('\\'Twas', 'it is')
    'It is'
    >>> keep_upper_case('sun', 'moon')
    'moon'

    :param old_word: first word
    :param new_word: second word
    :return: second word possibly capitalized
    """
    if old_word[0].isupper():
        new_word = new_word.capitalize()
    elif old_word[0] == '\'' and old_word[1].isupper():
        new_word = new_word.capitalize()
    return new_word

def capitalize_after_dot(poem):
    """
    Capitalizes line beginning words only in the beginning of sentences.

    >>> capitalize_after_dot('In Nineveh\\n\\
    ... And beyond Nineveh.\\n\\
    ... In the dusk\\n\\
    ... They were afraid.')
    'In Nineveh\\n\
and beyond Nineveh.\\n\
In the dusk\\n\
they were afraid.\\n'

    :param poem: text string
    """
    lines = poem.split('\n')
    capitalized = lines[0] + '\n'
    for i in range(1,len(lines)):
        if len(lines[i]) > 1:
            if lines[i][0].isupper():
                if lines[i-1] == '':
                    capitalized = capitalized + lines[i] + '\n'
                elif lines[i-1].endswith(('.', '!', '?')):
                    capitalized = capitalized + lines[i] + '\n'
                else:
                    capitalized = capitalized + lines[i][0].lower() +\
                                  lines[i][1:len(lines[i])] + '\n'
            else:
                capitalized = capitalized + lines[i] + '\n'
        else:
            capitalized = capitalized + lines[i] + '\n'
    return capitalized            

def capitalize_nnp(analysed):
    """
    Capitalizes proper nouns.

    >>> capitalize_nnp([('cat', 'NN'), ('helen', 'NNP')])
    [('cat', 'NN'), ('Helen', 'NNP')]
    
    :parameter analysed: list of word-tag tuples
    :return: list of word-tag tuples with the proper nouns capitalized
    """
    capitalized = []
    for word in analysed:
        if len(word) > 1:
            if word[1] == 'NNP':
                capitalized.append((word[0].capitalize(), word[1]))
            else:
                capitalized.append(word)
        else:
            capitalized.append(word)
    return capitalized

if __name__ == '__main__':
    import doctest
    doctest.testmod()
