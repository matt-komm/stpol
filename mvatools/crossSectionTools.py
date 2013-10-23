import csv
import os

def getCrossSection(name):
    """ Looks up the cross section from the header file """
    xsFile=os.path.join(os.environ["STPOL_DIR"], "src/headers","cross_sections.txt")
    xsf=open(xsFile)
    csvf=csv.DictReader(filter(lambda r: r[0]!='#', xsf))
    for r in csvf:
        if r['sample'] == name:
            return float(r[' xs'])

def getScaleFactor(dir,name,lumi):
    """ Calculates the proper scale factor for a sample based on cross section and processed events """
    xs=getCrossSection(name)
    f=open("%s/%s.count" % (dir,name))
    n=int(f.read())
    return xs*lumi/n
