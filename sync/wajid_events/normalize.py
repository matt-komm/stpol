import re
import sys

if __name__=="__main__":
    for line in sys.stdin.readlines():
        line = line.strip()
        spl = line.split("|")
        if len(spl)==6:
            print spl[1].strip()
