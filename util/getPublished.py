import re
import sys
if __name__=="__main__":
    for line in sys.stdin.readlines():
        match = re.match(".*=(.*/USER).*", line)
        if match:
            print match.group(1)
