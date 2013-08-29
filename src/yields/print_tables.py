from astropy.io import ascii
from astropy.table import Table, Column
import cPickle as pickle
from cutflow_table import order

latex_processes = {
    'diboson': 'Diboson',
    'wjets': r'\wjets',
    'dyjets': r'\zjets',
    'ttjets': r'\ttbar',
    'twchan': r'tW',
    'schan': r's-channel',
    'qcd': r'\QCD',
    'tchan': r't-channel',
    'mc': r'Total MC',
    'data': r'Data',
}

rownames = {
    'hlt+lep': "HLT, lepton",
    'met': r'\met / $m_{\ell\nu}$',
    'jet': '2 jets',
    'jet_rms': r'$RMS_{\text{j}}$',
    'tag': '1 tag',
    'mva': 'MVA',
    'bdt_fit': 'Fit',
}
processes_pretty = []
for k in order:
    k = k.lower()
    if k in latex_processes.keys():
        processes_pretty.append(latex_processes[k])
    else:
        processes_pretty.append(k)

def print_table(fname):
    tab = pickle.load(open(fname))
    data = Table()
    data.add_column(
        Column(data=processes_pretty, name='process')
    )
    for rowname, row in zip([t[0] for t in tab], tab):
        data.add_column(
            Column(data=row[1:], name=rownames[rowname])
        )
        data[rownames[rowname]].format = '%.0f'

    class MyLatex(ascii.Latex):
        def __init__(self, **kwargs):
            ascii.Latex.__init__(self, **kwargs)
            #self.header.data = ['process'] + order
            self.latex['header_start'] = '\hline'
            self.latex['header_end'] = '\hline'
            self.latex['preamble'] = r'\begin{center}'
            self.latex['tablefoot'] = r'\end{center}'
            self.latex['data_end'] = r'\hline'
            self.header.comment = r"\%Generated by src/yields/print_tables.py"

    ascii.write(data, Writer=MyLatex, latexdict = {'col_align':'|c|cccccc|c|'})
    import tabulate
    s = tabulate.tabulate(tab, tablefmt="orgtbl", numalign="center", floatfmt=".0f")
    while '  ' in s:
        s = s.replace('  ', ' ')
    print s