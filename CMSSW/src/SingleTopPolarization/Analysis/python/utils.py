def cap(s):
    return s[0:1].upper() + s[1:]

def prep(pref, x):
    if len(pref)>0:
        name = pref + cap(x)
    else:
        name = x
    return name

def sa(process, prefix, x, y):
    name = prep(prefix, x)
    setattr(process, name, y)
    return name

