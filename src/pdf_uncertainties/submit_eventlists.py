import sys
import os
from parse_input import *
from utils import pdfs
#Monkey-patch the system path to import the stpol header
sys.path.append(os.path.join(os.environ["STPOL_DIR"], "src/headers"))
from subprocess import call

data_files = get_data_files()
#pdfconfs = ["ct10", "nnpdf", "nnpdf_down", "nnpdf_up"] #,"mstw"]
    
for dataset, fileset in data_files.items():
        i = 0
        for (base_file, added_file) in fileset:
            bf_name = "/tmp/andres/evlist_pdf_%s_%d.sh" % (dataset, i)
            batch_outfile = open(bf_name, "w")
            batch_outfile.write("#!/bin/bash\n")
            batch_outfile.write("source $STPOL_DIR/setenv.sh\n")
            batch_outfile.write("python $STPOL_DIR/src/pdf_uncertainties/save_events.py " +dataset+ " " +str(i)+" "+base_file+" " + added_file + "\n")
            #print "python $STPOL_DIR/src/pdf_uncertainties/pdf_eventloop.py " +dataset+ " " +str(i)+" "+base_file+" " + added_file + "\n"
            batch_outfile.close()
            call(["chmod", "755", bf_name])
            suc = 1
            while not suc == 0:
                suc = call(["sbatch", "-x comp-d-058", bf_name])
                print bf_name, suc
                if not suc == 0:
                    print "XXX"
                    time.sleep(3)
            i+=1
        
