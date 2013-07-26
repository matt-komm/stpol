


import sys
s1 = r"""
\begin{tabular}{ |c|c|c| }
\hline
Process & cut-based & BDT  \\
\hline
""".strip()


def print_proc(pname, t1, e1, t2, e2):
	return "\n"+r"%s & %.1f $\pm$ %.1f  & %.1f $\pm$ %.1f \\"%(pname, t1, e1, t2, e2)

s2 = r"""
\ttbar    & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
\wjets    & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
\zjets    & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
\QCD      & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
Diboson   & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
tW        & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
s-channel & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
\hline
t-channel & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
\hline
Total MC  & FIXME $\pm$ FIXME  & FIXME $\pm$ FIXME \\
\hline
Data      & FIXME  & FIXME \\
\hline
""".strip()

s3 = "\n"+r"""
\end{tabular}
""".strip()

if __name__ == "__main__":
	vals = dict()
	for line1, line2 in zip(inf1.readlines(), inf2.readlines()):
		first_tot, first_err = parse_line(line1)
		second_tot, second_err = parse_line(line2)

	s2 = print_proc(r"\ttbar    ", 1.345, 2.34, 3.532, 4.345)
	s2 += print_proc(r"\wjets    ", 1.345, 2.34, 3.532, 4.345)
	s2 += print_proc(r"\zjets    ", 1.345, 2.34, 3.532, 4.345)
	s2 += print_proc(r"\QCD      ", 1.345, 2.34, 3.532, 4.345)
	s2 += print_proc(r"Diboson   ", 1.345, 2.34, 3.532, 4.345)
	s2 += print_proc(r"tW        ", 1.345, 2.34, 3.532, 4.345)
	s2 += print_proc(r"s-channel ", 1.345, 2.34, 3.532, 4.345)
	s2 += "\n" + r"\hline"
	s2 += print_proc(r"t-channel ", 1.345, 2.34, 3.532, 4.345)
	s2 += "\n" + r"\hline"
	s2 += print_proc(r"Total MC  ", 1.345, 2.34, 3.532, 4.345)
	s2 += "\n" + r"\hline"
	s2 += "\n" + r"Data       & %.1f  & %.1f \\" % (1.345, 2.34)


	print s1+s2+s3
