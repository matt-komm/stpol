from astropy.io import ascii
from astropy.table import Table
import cPickle as pickle

tab = pickle.load(open("results/yield_tables/cutflow_mu.pickle"))

tab[5] = tab[5][0:10]
tab[6] = tab[6][0:10]
#
data = Table({
    'process': len(tab[0])*['asd'],
    'HLT + lepton': tab[0],
    'MET/M_{t}(W)': tab[1],
    '2 jets': tab[2],
    'light jet rms': tab[3],
    '1 b-tag': tab[4],
    'MVA(BDT)': tab[5],
    'BDT fit': tab[6],

    },
    names=['process', 'HLT + lepton', 'MET/M_{t}(W)', '2 jets', 'light jet rms', '1 b-tag', 'MVA(BDT)', 'BDT fit']
)
ascii.write(data, Writer=ascii.Latex, latexdict = {'col_align':'c|ccccccccc'})
#import tabulate
#print tabulate.tabulate(tab)