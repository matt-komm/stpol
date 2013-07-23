import ROOT
import sys
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description='Prints the config file used to run the input step3 files.'
    )
    parser.add_argument('-f', dest='file',
        default=None, required=True,
        help="The input step3.root"
    )
    args = parser.parse_args()

    fi = ROOT.TFile(args.file)
    try:
        print fi.Get("trees/process_desc").GetTitle()
        print "Events_selected cutstring=",fi.Get("trees/Events_selected").GetTitle()
    except:
        print "Output is not recognizable as step3"
