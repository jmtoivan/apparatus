#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os, math, time, codecs
from collections import defaultdict

def entropy(elements):
	sum = 0
	for element in elements:
		sum += element

	result = 0.0;
	for x in elements:
		if x != 0:
			result += x * math.log(float(x)/float(sum))
	return -result

#k11 The number of times the two events occurred together
#k12 The number of times the second event occurred WITHOUT the first event
#k21 The number of times the first event occurred WITHOUT the second event
#k22 The number of times something else occurred (i.e. was neither of these events  

def logLikelihood(k11, k12, k21, k22):
	rowEntropy = entropy([k11, k12]) + entropy([k21, k22])
	columnEntropy = entropy([k11, k21]) + entropy([k12, k22])
	matrixEntropy = entropy([k11, k12, k21, k22])
	return 2 * (matrixEntropy - rowEntropy - columnEntropy)

target = sys.argv[1]
sep = ". "
if len(sys.argv) > 2:
	sep = sys.argv[2]

term_sentence = defaultdict(set)		
term_to_term = defaultdict(set)	
S = 0

f = codecs.open(target, "r", encoding = 'utf-8')
data = f.read()
f.close()

sentences = data.split(". ")
d = ""
for s in sentences:
	tokens = s.split(" ")
	tokens = sorted([f for f in tokens if len(f) > 2])

	for i in range(len(tokens)):
		terma = tokens[i]
		term_sentence[terma].add(S)
		for j in range(i+1, len(tokens)):
			termb = tokens[j]
			term_to_term[terma].add(termb)
	S += 1
	if S%1000 == 0:
		print 100*S/len(sentences),"% left"

print "Writing bg graph"
f = codecs.open("graph_sentence_nouns.txt", "w", encoding = 'utf-8')
f.write("term_a	term_b	ll_sen\n")	
counter = 0
target = len(term_to_term)
for i in term_to_term:
	neighbours = term_to_term[i]
	seni = term_sentence[i]
	
	for j in neighbours:
		senj = term_sentence[j]
		intersect = seni&senj
		
		k11 = len(intersect)
		k21 = len(seni-senj)
		k12 = len(senj-seni)
		k22 = S - len(seni|senj)
		ll = logLikelihood(k11, k12, k21, k22)

		f.write(i + "	" + j + "	" + str(ll) + "\n")
	
	counter += 1		
	if counter % 100 == 0:
		print (float(counter)/target)*100, "% done"
f.close()