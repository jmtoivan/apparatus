#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import networkx as nx
import cProfile
import re, codecs
import random
import tavuttaja_regexp as regexp
from bmgraph.file import Graph, Node, Edge

def main():
    
    f = codecs.open('/home/jmtoivan/Lemma_based_replace/graph_sentence_nouns.txt', encoding = 'utf-8')
    G = read_to_graph(f)

def read_to_graph(file_handle):
    G = nx.Graph()
    bmg = Graph()
    line = file_handle.readline()
    #Skip the first line
    line = file_handle.readline()
    keycounter = 0
    while line:
        l = line.split('\t')
        if len(l) < 3:
            line = file_handle.readline()
            continue
        l[2] = l[2].replace('\n', '')
        if len(l[0]) == 0 or len(l[1]) == 0:
            line = file_handle.readline()
            continue
        if l[2].replace('.', '').isdigit() == False:
            line = file_handle.readline()
            continue
        if float(l[2]) < 14:
            line = file_handle.readline()
            continue
        if l[0] not in G:
            G.add_node(regexp.clean(l[0]))
        if l[1] not in G:
            G.add_node(regexp.clean(l[1]))
        bmn1 = bmg.get_node(l[0].lower(), "Term")
        bmn2 = bmg.get_node(l[1].lower(), "Term")
        bme = bmn1.add_edge(bmn2)
        bme.type = "is_related_to"
        bme.attributes["llr"] = l[2]
        #G.add_edge(regexp.clean(l[0]), regexp.clean(l[1]))
        line = file_handle.readline()
        keycounter = keycounter + 1
        
    #print G.number_of_nodes()
    with codecs.open('/home/jmtoivan/Lemma_based_replace/temp.bmg', 'w', encoding = 'utf-8') as g:
        print >> g, unicode(bmg)

    #print nx.connected_components(G)
    #nx.draw(G)
    #plt.show()
    return G

def return_neighborhood(G, node, num_nodes):
    #for i in G:
        #l = G.neighbors(i)
        #print l
    l = G.neighbors(node)
    while len(l) > num_nodes:
        l.remove(l[random.randint(0,len(l)-1)])
    return l

if __name__ == '__main__':
    main()