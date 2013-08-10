import os

if __name__=="__main__":
    base = os.path.join(os.environ["STPOL_DIR"], "qcd_estimation", "fitted")
    for root, dirs, files in os.walk(base):
        if "fitted/mu" in root:
            lep = "mu"
        elif "fitted/ele" in root:
            lep = "ele"
        else:
            continue

        for fi in files:
            try:
                sf = float(open(os.path.join(root, fi)).readlines()[0].split(" ")[0])
            except Exception as e:
                print fi, e
            print "qcdScale['%s']['%s'] = %f" % (lep, fi.split(".")[0], sf)