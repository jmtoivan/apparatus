# -*- coding: utf-8 -*-
import os
import sys
import pty
import subprocess

from subprocess import PIPE
from contextlib import contextmanager

'''
Have conversations with launched processes, i.e. read and write without
closing the process.

@author Atte Hinkka <atte.hinkka@cs.helsinki.fi>

Easier subprocess handling.  This isn't very polished and definitely not very
general.  SlaveProcess should most probably work like subprocess.Popen and
have the same interface.  Just with the added benefit of actually working
properly.  This might be doable with *args, **kwargs and subclassing.

Usage:
from slave_process import SlaveProcess, slave_process

with slave_process(['foo']) as p:
    p.stdin.write('foo\n')
    p.stdin.flush()
    print p.stdout.readline()
    p.stdin.write('bar\n')
    p.stdin.flush()
    print p.stdout.readline()
'''


class SlaveProcess(object):
    def __init__(self, process, stdin, stdout):
        self.process = process
        self.stdin = stdin
        self.stdout = stdout

    def kill(self):
        os.kill(self.process.pid, 9)

@contextmanager
def slave_process(arg_list, stderr_to_stdout=True):
    if stderr_to_stdout != True:
        raise NotImplemented()

    master, slave = pty.openpty()
    p = subprocess.Popen(arg_list, stdin=PIPE, stdout=slave, stderr=slave)
    stdout = os.fdopen(master)

    slave_process = SlaveProcess(p, p.stdin, stdout)
    try:
        yield slave_process
    finally:
        slave_process.kill()
