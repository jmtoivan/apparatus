#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
import traceback
import StringIO

import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("bmgraph.file")


class NotImplementedError(Exception):
    pass

class mdict(dict):
    """This class implements a multi-value dictionary."""
    def __setitem__(self, key, value):
        self.setdefault(key, []).append(value)

    def __delitem__(self, key):
        raise NotImplementedError("del not supported for mdict, use .delete(k, v) instead")

    def delete(self, key, value):
        self[key].remove(value)

    def __str__(self):
        return unicode(self).encode('ASCII', 'backslashreplace')

    def __unicode__(self):
        pairs = []
        for key, values in self.items():
            for value in values:
                pairs.append("%s=%s" % (key, value.replace(" ", "+")))
        return u" ".join(pairs)


class GraphSink(object):
    def special_node_read(self, node_name, node_type):
        pass
    def edge_read(self, node1_name, node1_type,
                  node2_name, node2_type, type, attribute_dict):
        pass
    def node_attributes_read(self, node_name, node_type, attribute_dict):
        pass
    def comment_read(self, type, value):
        pass


class GraphObjectSink(GraphSink):
    '''Sink for an in-memory Graph object.  If passed a graph object as the kw
    param graph, append to that Graph.'''
    def __init__(self, graph=None):
        if graph != None:
            self.graph = graph
        else:
            self.graph = Graph()
    def special_node_read(self, node_name, node_type):
        self.graph.get_node(node_name, node_type).special_node = True
    def edge_read(self, node1_name, node1_type, node2_name, node2_type,
                  type, attribute_dict):
        n1 = self.graph.get_node(node1_name, node1_type)
        n2 = self.graph.get_node(node2_name, node2_type)
        e = n1.add_edge(n2)
        e.type = type
        for k, v in attribute_dict.iteritems():
            e.attributes[k] = v
    def node_attributes_read(self, node_name, node_type, attribute_dict):
        n = self.graph.get_node(node_name, node_type)
        for k, v in attribute_dict.iteritems():
            n.attributes[k] = v
    def get_object(self):
        return self.graph


class Graph(object):
    def __init__(self):
        self.attributes = mdict()
        self.nodes = {}
        self.comments = []

    def add_node(self, node):
        self.nodes[node.name] = node
    def del_node(self, node):
        del self.nodes[node.name]
    def get_node(self, name, type):
        if self.nodes.has_key(name):
            return self.nodes[name]
        else:
            n = Node(self, name, type)
            return n

    def __str__(self):
        print "called"
        return unicode(self).encode('ASCII', 'backslashreplace')

    def __unicode__(self):
        ret = []

        for node in self.nodes.values():
            if node.special_node:
                ret.append(unicode(node))
                specials_written = True

        for comment in self.comments:
            ret.append(u"# %s" % unicode(comment))
            comments_written = True

        written_edges = set([])
        for node in self.nodes.values():
            for edge in node.edges:
                if unicode(edge) in written_edges:
                    continue
                ret.append(unicode(edge))
                written_edges.add(unicode(edge))

        for node in self.nodes.values():
            if len(node.attributes.keys()) == 0:
                continue
            ret.append(u"# _attributes %s %s" % (unicode(node), unicode(node.attributes)))

        ret.append(u'')
        return u'\n'.join(ret)


class Edge(object):
    def __init__(self, n1, n2):
        self.attributes = mdict()
        self.n1 = n1
        self.n2 = n2

    def other(self, node):
        if node == self.n1:
            return self.n2
        return self.n1

    def __cmp__(self, other):
        return (str(self) == str(other))

    def __str__(self):
        return unicode(self).encode('ASCII', 'backslashreplace')

    def __unicode__(self):
        return u"%s %s %s %s" % (self.n1, self.n2, self.type, self.attributes)

    def __repr__(self):
        return "<Edge %s>" % str(self)


class Node(object):
    def __init__(self, graph, name, type):
        self.graph = graph
        self.attributes = mdict()
        self.name = name
        self.type = type
        self.special_node = False
        self.edges = []
        self.graph.add_node(self)

    def add_edge(self, other):
        e = Edge(self, other)
        self.edges.append(e)
        other.edges.append(e)
        return e

    def remove_edge(self, edge):
        self.edges.remove(edge)

    def delete(self):
        self.graph.del_node(self)
        for edge in self.edges:
            other = edge.other(self)
            other.remove_edge(edge)

    def __cmp__(self, other):
        return (str(self) == str(other))

    def __str__(self):
        return unicode(self).encode('ASCII', 'backslashreplace')

    def __unicode__(self):
        if self.type:
            return u"%s_%s" % (self.type, self.name)
        return self.name

    def __repr__(self):
        return "<Node %s>" % str(self)


def read_file(stream, sink):
    lines_read = 0
    for line in stream:
        lines_read += 1
        if logger.isEnabledFor(logging.INFO):
            if lines_read % 10000 == 0:
                logger.info("Read %i lines..." % lines_read)
            else:
                logger.debug("Read %i lines..." % lines_read)
        if len(line) < 1:
            continue

        # Decode early
        try:
            pass
            # line = line.decode('utf-8', 'replace')
        except Exception, e:
            print lines_read, line.replace("\n", "")
            traceback.print_exc()
            raise e

        if line[0] == '#':
            comment_type, value = line[2:].split(" ", 1)
            # only handles node attributes atm...
            if comment_type == "_attributes":
                node, attributes = value.split(" ", 1)

                parts = node.split('_', 1)

                if len(parts) == 1:
                    node_name = parts[0]
                    node_type = None
                else:
                    node_name = parts[1]
                    node_type = parts[0]

                attributes = attributes.split(" ")
                attr_dict = {}
                for attribute in attributes:
                    try:
                        key, value = attribute.split("=", 1)
                        attr_dict[key] = value.replace("\n", "").replace("+", " ")
                    except ValueError, ve:
                        logger.warning("Line %i: error parsing attribute %s" % (lines_read, attribute))
                        logger.warning(traceback.format_exc())
                sink.node_attributes_read(node_name, node_type, attr_dict)
            else:
                sink.comment_read(comment_type, value.replace("\n", "").replace("+", " "))

        else:
            parts = line.split(" ", 2)
            if len(parts) == 1:
                if parts[0].strip() == "":
                    continue
                parts = parts[0].replace("\n", "").split("_", 1)
                if len(parts) == 1:
                    sink.special_node_read(parts[0], None)
                else:
                    sink.special_node_read(parts[1], parts[0])
            if len(parts) == 3:
                attr_dict = {}
                edge_attributes = parts[2].replace("\n", "").split(" ")
                type = edge_attributes[0]
                if len(edge_attributes) > 0:
                    for attr in edge_attributes[1:]:
                        try:
                            key, value = attr.split("=", 1)
                            attr_dict[key] = value.replace("+", " ")
                        except ValueError, ve:
                            logger.warning("Line %i: error parsing attribute %s" % (lines_read, attr))
                            logger.warning(traceback.format_exc())

                n1_parts = parts[0].split('_', 1)

                if len(n1_parts) == 1:
                    n1_name = n1_parts[0]
                    n1_type = None
                else:
                    n1_name = n1_parts[1]
                    n1_type = n1_parts[0]

                n2_parts = parts[1].split('_', 1)
                if len(n2_parts) == 1:
                    n2_name = n2_parts[0]
                    n2_type = None
                else:
                    n2_name = n2_parts[1]
                    n2_type = n2_parts[0]

                sink.edge_read(n1_name, n1_type, n2_name, n2_type,
                               type, attr_dict)

def read_string(string, sink):
    return read_file(StringIO.StringIO(string), sink)

def main(args):
    if len(args) > 0:
        s = bmgraph_file.GraphObjectSink()
        for arg in args:
            try:
                bmgraph_file.read_file(arg, s)
            except:
                traceback.print_exc()
        print s.get_object()
    else:
        print "Please run test.py to run tests."

if __name__ == '__main__':
    main(sys.argv[1:])
