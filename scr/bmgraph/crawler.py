# -*- coding: utf-8 -*-

import os
from os import environ as env
from os.path import join as path_join
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from optparse import OptionParser

_crawler_params = {
    'maxdepth': None,
    'maxnodedegree': None,
    'node_exclude_file': None,
    'node_include_file': None,
    'mode': None, # [connection_subgraph, neighborhood]
    'mingoodness': None,
    'initial_min_goodness': None,
    'max_st_nodes': None,
    'min_st_nodes': None,
    'max_st_pairs': None,
    'max_nodes': None,
    'max_nodes_post': None,
    'min_nodes': None,
    'max_query_time': 5,
    'single_connected_component': None,
    'eliminate_spurious_paths': None,
    'eliminate_redundant_links': None,
    'do_not_eliminate_spurious_paths': None,
    'no_acyclic_filter': None,
    'adjust_goodness_pairwise': None,
    'all_best_paths': None,
    'best_paths_only': None,
    'output_degrees': None,
    'do_not_output_degrees': None,
    'prune_by_gub': None,
    'boost_trivial_links': None,
    }

def crawl_bmg(bmg_file, out_file, work_dir, query_nodes, params={}):
    if not os.path.exists(work_dir):
        raise Exception("Work directory %s doesn't exist." % work_dir)
    elif len(query_nodes) == 0:
        raise Exception("No query nodes defined.")

    log_file_handle = open(path_join(work_dir, 'log.txt'), 'w')
    print >> log_file_handle, "# Working in %s" % work_dir

    for k, v in _crawler_params.iteritems():
        if k == 'maxdepth':
            continue
        if v != None and not params.has_key(k):
            params[k] = v

    e = ['crawler']
    for pair in [('-logfile', 'log.txt'),
                 ('-graphfile', bmg_file),
                 ('-outfile', out_file)]:
        e.append(pair[0])
        e.append(pair[1])

    for k, v in params.iteritems():
        if v != None:
            e.append('-%s' % k)
            e.append(str(v))

    if params.has_key('maxdepth') and params['maxdepth'] != None:
        e.append(params['maxdepth'])

    print >> log_file_handle, "# Executing: %s" % e
    p = Popen(e, bufsize=0, cwd=work_dir, stdin=PIPE, stderr=PIPE)
    stderr, stdout = p.communicate(" ".join(query_nodes))
    print >> log_file_handle, stderr
    log_file_handle.close()

    result = p.poll()
    return result


def main():
    parser = OptionParser(usage='Reads query nodes from stdin and outputs to stdout.')
    parser.add_option("-b", "--bmg", dest="bmg",
                      help="BMGraph file to Crawl",
                      metavar="BMGRAPH-FILE")
    parser.add_option("-o", "--output-bmg", dest="out_bmg",
                      help="BMGraph file to Crawl to",
                      metavar="BMGRAPH-FILE")
    parser.add_option("-q", "--query-nodes", dest="query_nodes",
                      help="Query nodes")
    opts, args = parser.parse_args()
    if not opts.bmg:
        parser.error("BMGraph file required!")
    elif not opts.query_nodes:
        parser.error("Query nodes required!")
    elif not opts.out_bmg:
        parser.error("BMGraph output file required!")

    prefs = {}
    crawl_bmg(opts.bmg, opts.out_bmg, os.getcwd(),
              opts.query_nodes.split(" "))
    print 'Log written to log.txt.'


if __name__ == '__main__':
    main()
