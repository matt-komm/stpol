#!/bin/sh
echo "root wrapper, sourcing..."
source /Users/joosep/Documents/root/bin/thisroot.sh
echo "root wrapper, running $@"
$@
echo "root wrapper is done..."
exit 0

