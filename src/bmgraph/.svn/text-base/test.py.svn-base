#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import unittest
runner = unittest.TextTestRunner(stream=sys.stderr, descriptions=True, verbosity=2)

import db as bmgraph_db
import file as bmgraph_file


class Test_mdict(unittest.TestCase):
    def setUp(self):
        self.m = bmgraph_file.mdict()
        self.m["k"] = "v"
        self.m["k"].append("foo")

    def test_keys(self):
        self.assertTrue(self.m.has_key("k"))
        self.assertTrue("foo" in self.m["k"])
        self.assertTrue("v" in self.m["k"])

    def test_delete(self):
        self.m.delete("k", "v")
        self.assertTrue("v" not in self.m["k"])


class TestStringReading(unittest.TestCase):
    def setUp(self):
        self.text = """CellularComponent_GO:GO:0009531 CellularComponent_GO:GO:0009505 is_a best=0 goodness=0.677396 rarity=0.8467 relevance=0.8 reliability=1 source_db_name=GO source_db_version=2010-05-26_19:30
CellularComponent_GO:GO:0048196 CellularComponent_GO:GO:0009531 -is_a best=0 goodness=0.677396 rarity=0.8467 relevance=0.8 reliability=1 source_db_name=GO source_db_version=2010-05-26_19:30

# _attributes CellularComponent_GO:GO:0048196 source_db_name=GO foo=bar
"""
        s = bmgraph_file.GraphObjectSink()
        bmgraph_file.read_string(self.text, s)
        self.graph = s.get_object()

    def test_read(self):
        self.assertTrue(self.graph is not None)

    def test_node_count(self):
        self.assertEqual(3, len(self.graph.nodes.values()))

    def test_edge_count(self):
        edges = set()
        for node in self.graph.nodes.values():
            for edge in node.edges:
                edges.add(edge)
        self.assertEqual(2, len(edges))


class TestSuggestAttributes(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        bmgraph_db.logger.setLevel(logging.INFO)
        
        g = u"""

"""
        self.bmg_file = "/tmp/bmgdb_test_%i.bmg" % os.getpid()
        with codecs.open(filename, 'w', encoding="utf-8") as f:
            print >> f, g
        bmgraph_db.build_db(conn, self.bmg_file)

    def tearDown(self):
        self.conn.close()
        try:
            os.unlink(self.bmg_file)
        except:
            pass

def main():
    unittest.main(testRunner=runner)

if __name__ == '__main__':
    main()

