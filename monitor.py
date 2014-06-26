#!/usr/bin/env python

def usage():
    print "Usage:"
    print "monitor.py prog file"
    print "  prog - the program to call"
    print "  file - the file to monitor"

if __name__ == '__main__':
    import os
    import subprocess
    import sys
    import time

    try:
        prog = sys.argv[1]
        f = sys.argv[2]
        if not os.path.isfile(f):
            usage()
            exit(1)
        f = os.path.abspath(f)
    except IOError:
        usage()
        exit(1)
    except IndexError:
        usage()
        exit(1)

    old = os.path.getctime(f)
    new = 0

    subprocess.call(['clear'])
    print ""
    print "Waiting on " + os.path.basename(f) + " ..."
    print ""

    while True:
        time.sleep(1)
        try:
            new = os.path.getctime(f)
        except:
            continue
        if new - old:
            print "Executing " + prog + " " + f
            print "" 
            old = new
            subprocess.call([prog, f])
            print ""
            print "Waiting on " + os.path.basename(f) + " ..."
            print ""
