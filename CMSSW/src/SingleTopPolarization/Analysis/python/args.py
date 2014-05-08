import sys

def inArgs(s):
    r = False
    if s in sys.argv:
        sys.argv.remove(s)
        r = True
    return r

def getArg(argName, default=None, conv=int):
	f = filter(lambda x: x.startswith(argName), sys.argv)
	if len(f) != 1:
		return default
	sys.argv.remove(f[0])
	argVal = f[0].split("=")[1]
        argVal = conv(argVal)
	return argVal
	return default
