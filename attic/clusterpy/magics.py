#Define a magic that runs the cell locally and remotely
def pxlocal(line, cell):
    ip = get_ipython()
    ip.run_cell_magic("px", line, cell)
    ip.run_cell(cell)

get_ipython().register_magic_function(pxlocal, "cell")
