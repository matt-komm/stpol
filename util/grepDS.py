#!/usr/bin/env python
import re,sys

pat = re.compile(".*=(/.*/USER).*")
if __name__=="__main__":
    for li in sys.stdin.readlines():
        m = pat.match(li)
        if m:
            print m.group(1)
