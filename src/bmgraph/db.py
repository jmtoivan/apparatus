#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("bmgraph.db")

import traceback
from optparse import OptionParser
from pprint import pprint
import UserDict
import codecs

import sqlite3

import file as bmgraph_file

_utf8_out = codecs.getwriter('utf-8')(sys.stdout)


def levenshtein(a, b):
    a = a.lower()
    b = b.lower()
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


class NotImplemented(Exception):
    pass

class NodeAttributeProxyDict(bmgraph_file.mdict, UserDict.DictMixin):
    def __init__(self, node_id, connection):
        self._node_id = node_id
        self._connection = connection
        self._populated = False

    # __getitem__(), __setitem__(), __delitem__(), and keys()
    def __getitem__(self, key):
        self.populate()
        return self[name]

    def __setitem__(self, key, value):
        self.setdefault(key, []).append(value)

    def __delitem__(self, key):
        raise NotImplemented()

    def keys(self):
        self.populate()
        return dict.keys(self)

    def populate(self):
        if self._populated is True:
            return
        c = self._connection.cursor()
        q = ('SELECT * FROM node_attribute WHERE node_id=?;', (self._node_id,))
        c.execute(*q)
        for row in c:
            if row['text_value'] != None:
                self[row['name']] = row['text_value']
            elif row['bool_value'] != None:
                self[row['name']] = row['bool_value']
        self._populated = True
        c.close()


class EdgeAttributeProxyDict(bmgraph_file.mdict, UserDict.DictMixin):
    def __init__(self, edge_id, connection):
        self._edge_id = edge_id
        self._connection = connection
        self._populated = False

    # __getitem__(), __setitem__(), __delitem__(), and keys()
    def __getitem__(self, key):
        self.populate()
        return self[name]

    def __setitem__(self, key, value):
        self.setdefault(key, []).append(value)

    def __delitem__(self, key):
        raise NotImplemented()

    def keys(self):
        self.populate()
        return dict.keys(self)

    def populate(self):
        if self._populated is True:
            return
        c = self._connection.cursor()
        q = ('SELECT * FROM edge_attribute WHERE edge_id=?;', (self._edge_id,))
        c.execute(*q)
        for row in c:
            if row['text_value'] != None:
                self[row['name']] = row['text_value']
            elif row['bool_value'] != None:
                self[row['name']] = row['bool_value']
        self._populated = True
        c.close()


class Node(object):
    def __init__(self, id, connection):
        self.id = id
        self.connection = connection
        self._populated = False
        self.attributes = NodeAttributeProxyDict(id, connection)

    def __getattribute__(self, name):
        if (name == 'an' or name == 'type') and self._populated == False:
            c = self.connection.cursor()
            q = ('SELECT an, type FROM node WHERE id=?;', (self.id,))
            c.execute(*q)
            self._an, self._type = c.fetchone()
        if name == 'type':
            return self._type
        if name == 'an':
            return self._an
        return object.__getattribute__(self, name)

    def __repr__(self):
        return "<Node #%i %s>" % (self.id, self.__repr__())

    def __str__(self):
        return unicode(self).encode('ASCII', 'backslashreplace')

    def __unicode__(self):
        attrs = []
        for k, v in self.attributes.iteritems():
            for i in v:
                attrs.append("%s=%s" % (k, i.replace(' ', '+')))
        return "# _attributes %s_%s %s" % (self.type, self.an, " ".join(attrs))

    def typed_name(self):
        return u"%s_%s" % (self.type, self.an)

    def __eq__(self, other):
        if hasattr(other, 'id'):
            if self.id == other.id:
                return True
        return False
    def __hash__(self):
        return self.id


class Edge(object):
    def __init__(self, id, n1_id, n2_id, type, connection):
        self._id = id
        self.n1 = Node(n1_id, connection)
        self.n2 = Node(n2_id, connection)
        self.type = type
        self._connection = connection
        self._populated = False
        self.attributes = EdgeAttributeProxyDict(id, connection)

    def __repr__(self):
        return "<Edge #%i %s>" % (self.id, self.__repr__())

    def __str__(self):
        return unicode(self).encode('ASCII', 'backslashreplace')
    def __unicode__(self):
        attrs = []
        for k, v in self.attributes.iteritems():
            for i in v:
                attrs.append("%s=%s" % (k, i.replace(' ', '+')))
        return u"%s %s %s %s" % (self.n1.typed_name(),
                                 self.n2.typed_name(),
                                 self.type, " ".join(attrs))
    def __eq__(self, other):
        if hasattr(other, '_id'):
            if self._id == other._id:
                return True
        return False


def create_db(cursor):
    create_statements = (
        '''CREATE TABLE node (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- unique identification for a node, used to reference other tables
        an text,
        -- actual accession number, a textual property
        type text
        )''',
        '''CREATE UNIQUE INDEX id_i ON node (id);''',
        '''CREATE UNIQUE INDEX an_i ON node (an);''',

        '''CREATE TABLE edge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- unique identification for a node, used to reference other tables
        n1_id integer,
        n2_id integer,
        type text
        )''',
        '''CREATE INDEX n1_id_i ON edge (n1_id);''',
        '''CREATE INDEX n2_id_i ON edge (n2_id);''',

        '''CREATE TABLE node_attribute (
        node_id INTEGER,
        name TEXT,
        bool_value TEXT,
        text_value TEXT
        )''',
        '''CREATE INDEX node_attr_i ON node_attribute (node_id);''',

        '''CREATE TABLE edge_attribute (
        edge_id INTEGER,
        name TEXT,
        bool_value TEXT,
        text_value TEXT
        )''',
        '''CREATE INDEX edge_attr_i ON edge_attribute (edge_id);''',
        )
    for stmt in create_statements:
        # print stmt
        cursor.execute(stmt)


class BMGraphDBSink(bmgraph_file.GraphSink):
    def __init__(self, connection):
        super(BMGraphDBSink, self).__init__()
        self.connection = connection
        self.cursor = connection.cursor()

    def resolve_node_id(self, an, node_type):
        self.cursor.execute('SELECT id FROM node WHERE an=?;', (an,))
        ret = self.cursor.fetchone()
        if ret != None:
            return ret[0]

    def get_or_create_node_id(self, an, node_type):
        node_id = self.resolve_node_id(an, node_type)
        if node_id != None:
            return node_id
        self.cursor.execute('INSERT INTO node (an, type) VALUES (?, ?);', (an, node_type))
        return self.resolve_node_id(an, node_type)

    def special_node_read(self, an, node_type):
        node_id = self.get_or_create_node_id(an, node_type)

        q = ('SELECT bool_value FROM node_attribute WHERE node_id=? AND name=?;', (node_id, 'special'))
        self.cursor.execute(*q)
        if self.cursor.fetchone() != None:
            q = ('UPDATE node_attribute SET bool_value=? WHERE node_id=? AND name=?;',
                 (True, node_id, 'special'))
            self.cursor.execute(*q)
        else:
            q = ('INSERT INTO node_attribute (node_id, name, bool_value) VALUES (?,?,?);',
                 (node_id, 'special', True))
            self.cursor.execute(*q)

    def edge_read(self, node1_name, node1_type, node2_name, node2_type,
                  type, attribute_dict):
        n1_id = self.get_or_create_node_id(node1_name, node1_type)
        n2_id = self.get_or_create_node_id(node2_name, node2_type)

        q = ('INSERT INTO edge (n1_id, n2_id, type) VALUES (?,?,?);',
             (n1_id, n2_id, type))
        self.cursor.execute(*q)
        edge_id = self.cursor.lastrowid

        for k, v in attribute_dict.iteritems():
            q = ('INSERT INTO edge_attribute (edge_id, name, text_value) VALUES (?,?,?);',
                 (edge_id, k, v))
            self.cursor.execute(*q)
    def node_attributes_read(self, an, node_type, attribute_dict):
        node_id = self.get_or_create_node_id(an, node_type)

        for k, v in attribute_dict.iteritems():
            q = ('INSERT INTO node_attribute (node_id, name, text_value) VALUES (?,?,?);',
                 (node_id, k, v))
            self.cursor.execute(*q)


def node_count(cursor):
    cursor.execute('SELECT count(id) FROM node;')
    return cursor.fetchone()[0]
def node_attribute_count(cursor):
    cursor.execute('SELECT count(*) FROM node_attribute;')
    return cursor.fetchone()[0]
def edge_attribute_count(cursor):
    cursor.execute('SELECT count(*) FROM edge_attribute;')
    return cursor.fetchone()[0]
def edge_count(cursor):
    cursor.execute('SELECT count(*) FROM edge;')
    return cursor.fetchone()[0]


def suggest(connection, pattern, fields, print_results=False):
    "suggestion pattern and attribute names to look for"
    attr_names = []
    for field in fields:
        attr_names.append('name=?')

        if len(attr_names) > 0:
            r = u"SELECT node_id FROM node_attribute"
        r = r + u" WHERE text_value like '%' || ? || '%'"
        r = r + u" AND " + " AND ".join(attr_names) + u";"
        l = list(fields)
        l.insert(0, pattern)
        q = (r, tuple(l))
        # print q
    else:
        q = (u'SELECT node_id FROM node_attribute WHERE text_value like \'%\' || ? || \'%\';',
             (pattern,))

    ret = set()

    c = connection.cursor()
    c.execute(*q)

    if c.rowcount < 1:
        q = (u'SELECT id FROM node WHERE an like \'%\' || ? || \'%\';',
             (pattern,))
        c.execute(*q)

    for row in c:
        n = Node(row[0], connection)
        ret.add(n)

    if print_results == True:
        print_order = []
        for n in ret:
            n.attributes.populate()
            if len(n.attributes) == 0:
                print_order.append((n.an, n))
            else:
                break_this = False
                for k, vals in n.attributes.iteritems():
                    for val in vals:
                        if pattern in val:
                            print_order.append((val, n))
                            break_this = True
                        if break_this:
                            break
                    if break_this:
                        break

        levenshtein_order = []
        for t in print_order:
            levenshtein_order.append((levenshtein(pattern, t[0]), t[1]))

        # levenshtein_order = sorted(levenshtein_order, key=lambda i: i[0])
        levenshtein_order.sort(key=lambda i: i[0])

        for distance, node in levenshtein_order:
            _utf8_out.write(u"%s\n" % node)

    return ret


def edges(connection, an, print_results=False):
    c = connection.cursor()
    c.execute('SELECT id FROM node WHERE an=?;', (an,))
    ret = c.fetchone()
    if ret is None:
        return

    node_id = ret[0]
    node = Node(node_id, connection)
    node.attributes.populate()
    # Special node
    if print_results:
        _utf8_out.write(u"%s\n" % node.typed_name())

    nodes = set()
    c.execute('SELECT DISTINCT id, n1_id, n2_id, type FROM edge WHERE n1_id=? OR n2_id=?;',
              (node_id, node_id))

    ret = set()
    for row in c:
        e = Edge(row['id'], row['n1_id'], row['n2_id'], row['type'], connection) 
	#Take also llr-values, (previous version did not have the next line): 
	e.attributes.populate()       
	ret.add(e)
	
        if print_results:
            e.attributes.populate()
            nodes.add(e.n1)
            nodes.add(e.n2)
            _utf8_out.write(u"%s\n" % e)

    if print_results:
        for n in nodes:
            n.attributes.populate()
            _utf8_out.write(u"%s\n" % n)
    
    return ret


def sample(connection, count, constraints=None, print_results=False):
    """
    count is the number of samplable nodes,
    constraint contains the attributes that must match the nodes returned.
    """
    c = connection.cursor()

    if constraints is not None:
        raise NotImplemented()


    # Special case for count > node count in db
    c.execute("SELECT COUNT(id) FROM node;")
    if count >= c.fetchone()[0]:
        c.execute("SELECT id FROM node;")
        ret = []
        for row in c:
            n = Node(row[0], connection)
            ret.append(n)
            if print_results:
                n.attributes.populate()
                _utf8_out.write(u"%s\n" % n.typed_name())
        return ret


    ids = set()
    for i in range(count):
        while True:
            q = "SELECT id FROM node WHERE id >= (abs(random()) % (SELECT max(id) FROM node)) LIMIT 1;"
            c.execute(q,)
            id = c.fetchone()[0]
            if id not in ids:
                ids.add(id)
                break

    ret = []
    for id in ids:
        n = Node(id, connection)
        ret.append(n)
        if print_results:
            n.attributes.populate()
            _utf8_out.write(u"%s\n" % n.typed_name())
    return ret


def build_db(connection, filename):
    c = connection.cursor()
    create_db(c)
    with codecs.open(filename, 'r', encoding="utf-8") as f:
        s = BMGraphDBSink(connection)
        # bmgraph.logger.setLevel(logging.DEBUG)
        bmgraph_file.logger.setLevel(logging.INFO)
        bmgraph_file.read_file(f, s)
    connection.commit()
    logger.info("%i rows in the database." % node_count(c))
    logger.info("%i node attributes in the database." % node_attribute_count(c))
    logger.info("%i edge attributes in the database." % edge_attribute_count(c))
    logger.info("%i edges in the database." % edge_count(c))