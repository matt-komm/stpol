from astropy.io import ascii
from astropy.table import Table, Column
import cPickle as pickle
from cutflow_table import order

def print_table(fname):
    tab = pickle.load(open(fname))
    data = Table()
    data.add_column(
        Column(data=9*['row'], name='process')
    )
    for rowname, row in zip([t[0] for t in tab], tab):
        data.add_column(
            Column(data=row[1:], name=rowname)
        )
        data[rowname].format = '%.2f'

    ascii.write(data, Writer=ascii.Latex, latexdict = {'col_align':'c|ccccccccc'})
    import tabulate
    s = tabulate.tabulate(tab, tablefmt="orgtbl", numalign="center", floatfmt=".0f")
    while '  ' in s:
        s = s.replace('  ', ' ')
    print s