import itertools
from collections import deque

def flatten(l):
    l2 = [([x] if isinstance(x,str) or isinstance(x, tuple) else x) for x in l]
    return list(itertools.chain(*l2))
t = ("root",[
    ("childA", "leaf1"),
    ("childB", [
        ("ccA", "leaf2"),
        ("ccB", [
            ("cccA", "leaf4")
        ])
    ])
])

def isNode(node):
    return isinstance(node, tuple) and len(node)==2

def isNodeList(l):
    isl = isinstance(l, list)
    if not isl:
        return isl
    for n in l:
        isl = isl and isNode(n)
    return isl

def isLeaf(node):
    #return isinstance(node[1], basestring)
    return not (isNode(node[1]) or isNodeList(node[1]))

# def getNode(root, nodelist):
#     print "+", root, nodelist
#     if len(nodelist)==0:
#         return root[1][0]
#     nodename = nodelist.popleft()
#     parname, children = root
#     if parname==nodename:
#         return itertools_flatten([getNode((name, nodes), nodelist) for name, nodes in children if name==nodename])

def getPathLeaves(root, path=''):
    assert(isNode(root))
    name, children = root
    if path:
        _path = path + "." + name
    else:
        _path = name
    if isLeaf(root):
        return (_path, children)
    assert(isNodeList(children))
    return flatten([getPathLeaves(child, _path) for child in children])

if __name__=="__main__":
    print getPathLeaves(t)
    #print getNode(t, deque(["childA"]))
    #for x in yield_odd_numbers(10):
    #    print x