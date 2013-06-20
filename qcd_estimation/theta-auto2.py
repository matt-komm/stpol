#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path, datetime, re, sys, copy, traceback, shutil, hashlib, tempfile
from theta_auto import *

def clean_workdir():
    shutil.rmtree(config.workdir, ignore_errors = True)
    setup_workdir()

def setup_workdir():
    if not os.path.exists(config.workdir): os.mkdir(config.workdir)
    if not os.path.exists(os.path.join(config.workdir, 'plots')): os.mkdir(os.path.join(config.workdir, 'plots'))

def main():
    scriptname = 'analysis.py'
    tmpdir, profile = False, False
    for arg in sys.argv[1:]:
        if '.py' in arg:
            scriptname = arg
            sys.argv.pop(sys.argv.index(arg))
        if arg=='--tmpdir': tmpdir = True
        if arg=='--profile': profile = True
    if tmpdir:
        config.workdir = tempfile.mkdtemp()
    else:
        config.workdir = os.path.join(os.getcwd(), scriptname[:-3])
        config.workdir = os.path.realpath(config.workdir)
    setup_workdir()
    config.theta_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    config.report = html_report(os.path.join(config.workdir, 'index.html'))
    variables = globals()
    variables['report'] = config.report
    utils.info("executing script %s" % scriptname)
    utils.info("argv=" + str(sys.argv))
    try:
        if profile:
            import cProfile
            cProfile.runctx("execfile(scriptname, variables)", globals(), locals())
        else:
            execfile(scriptname, variables)
    except Exception as e:
        print "error while trying to execute analysis script %s:" % scriptname
        traceback.print_exc()
        sys.exit(1)
    utils.info("workdir is %s" % config.workdir)

if __name__ == '__main__': main()

