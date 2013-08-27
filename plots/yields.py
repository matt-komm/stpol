#FIXME
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

def parse_line(l):
	samp, tot, err = map(lambda x: x.strip(), l.split("|"))
	return samp, float(tot), float(err)

if __name__ == "__main__":
	vals = dict()

	inf1 = open(sys.argv[1])
	inf2 = open(sys.argv[2])

	for line1, line2 in zip(inf1.readlines(), inf2.readlines()):
		samp, first_tot, first_err = parse_line(line1)
		samp, second_tot, second_err = parse_line(line2)
		vals[samp.lower()] = first_tot, first_err, second_tot, second_err

	s2 = print_proc(r"\ttbar    " , *vals["ttjets"])
	s2 += print_proc(r"\wjets    ", *vals["wjets"])
	s2 += print_proc(r"\zjets    ", *vals["dyjets"])
	s2 += print_proc(r"\QCD      ", *vals["qcd"])
	s2 += print_proc(r"Diboson   ", *vals["diboson"])
	s2 += print_proc(r"tW        ", *vals["twchan"])
	s2 += print_proc(r"s-channel ", *vals["schan"])
	s2 += "\n" + r"\hline"
	s2 += print_proc(r"t-channel ", *vals["tchan"])
	s2 += "\n" + r"\hline"
	s2 += print_proc(r"Total MC  ", *vals["mc"])
	s2 += "\n" + r"\hline"
	s2 += "\n" + r"Data       & %.1f  & %.1f \\" % (vals["data"][0], vals["data"][2])
	s2 += "\n" + r"\hline"

	print s1+s2+s3
