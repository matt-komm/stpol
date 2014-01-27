#!/usr/bin/python
slope=1.0
n=7
for i in range(n):
    edge=-1.0+2.0*(1.0*i/n)*(1.0*i/n*2*(1-slope))
    print edge
