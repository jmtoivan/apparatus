#!/usr/bin/python

# USAGE: pair2bmgraph.py [-ew 3] [-rc resource] < txt-file > bmg-file
# Outputs a bmg-file from a raw input : 
#    std input gives a list of weighted edges :
#      nodeA nodeB (list of attributes values)
#    (1 edge per line)
# default : takes 3rd field of each line as weight value
# -ew n : takes the n_th field as weight for each edge
# -rc file : file that sets up default values, types .....
# by default : file in the same directory as this program.

import sys
from ConfigParser import ConfigParser
from os import path

RESOURCE = path.abspath(sys.modules['__main__'].__file__).rpartition(".")[0]+".rc"

def usage():
        print "USAGE:",sys.argv[0]," [-ew 3] [-rc resource] < txt-file > bmg-file"
	print "Outputs a bmg-file from a raw input :" 
	print "    std input gives a list of weighted edges :"
	print "      nodeA nodeB (list of values)  --  (1 edge per line)"
	print "OPTIONS:"
	print "    -ew n : takes the n_th field as weight for each edge"
	print "            default : 3rd field of each line is weight value"
	print "    -rc file : read file as a resource file"
	print "               settings for edge, node types, fieldnumber, lines to ignore ..."
	print "               default resource : "+RESOURCE
        print " PREDEFINED INFOS will be added (see default resource file)"

	sys.exit()

if len(sys.argv) > 5 or len(sys.argv) == 4 or len(sys.argv) == 2 : usage()

if len(sys.argv) == 3 :
	if sys.argv[1] == "-rc" : RESOURCE = int(sys.argv[2])
if len(sys.argv) == 5 :
	if sys.argv[3] == "-rc" : RESOURCE = int(sys.argv[4])

config = ConfigParser()
config.read([RESOURCE])

EDGEWEIGHT=int(config.get("infoGiven","edgeweight"))
NODEA=int(config.get("infoGiven","nodeA"))
NODEB=int(config.get("infoGiven","nodeB"))

NODETYPE=config.get("infoAdded","nodetype")
EDGETYPE=config.get("infoAdded","edgetype")
VALUETYPE=config.get("infoAdded","edgeattribute")
EDGECOLOR=config.get("infoAdded","edgecolor")

## if found special motif then skip the line
NOTFOUND=config.get("ignoredLine","ignoredfield")
COMMENT=config.get("ignoredLine","comment")

BMGEDGESPECIALLINE="# _symmetric "+EDGETYPE

if len(sys.argv) == 3 :
	if sys.argv[1] == "-ew" : EDGEWEIGHT = int(sys.argv[2])
if len(sys.argv) == 5 :
	if sys.argv[3] == "-ew" : EDGEWEIGHT = int(sys.argv[4])

print BMGEDGESPECIALLINE	

MINLENGTH=max(EDGEWEIGHT,max(NODEA,NODEB))
for line in sys.stdin:
	if line.find(COMMENT) >= 0: continue	
        w = line.split()
	if len(w) >= MINLENGTH :
		if w[EDGEWEIGHT-1].find(NOTFOUND) < 0:
			print NODETYPE+"_"+w[NODEA-1], NODETYPE+"_"+w[NODEB-1], EDGETYPE, VALUETYPE+"="+w[EDGEWEIGHT-1], "fill="+EDGECOLOR
