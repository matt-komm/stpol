#FIXME
import sys
import datetime

s1 = r"""
\begin{table}
\begin{center}

\begin{tabular}{ |c|c|c| }
\hline
Process & Muon channel & Electron channel  \\
\hline
""".strip() #To remove newlines at start and end

# \ttbar     & 663.2 $\pm$ FIXME  & 446.6 $\pm$ FIXME \\
# tW         & 51.8 $\pm$ FIXME  & 30.5 $\pm$ FIXME \\
# s-channel  & 21.7 $\pm$ FIXME  & 15.8 $\pm$ FIXME \\
# \hline
# \wjets     & 1298.6 $\pm$ FIXME  & 1154.9 $\pm$ FIXME \\
# \zjets     & 105.7 $\pm$ FIXME  & 68.3 $\pm$ FIXME \\
# Diboson    & 22.4 $\pm$ FIXME  & 16.1 $\pm$ FIXME \\
# \hline
# \QCD       & 82.2 $\pm$ FIXME  & 95.9 $\pm$ FIXME \\
# \hline
# t-channel  & 2325.6 $\pm$ FIXME  & 2341.0 $\pm$ FIXME \\
# \hline
# Total Expected   & 4571.2 $\pm$ FIXME  & 4169.2 $\pm$ FIXME \\
# \hline
# Data       & 4704.0  & 4303.0 \\

s3 = "\n"+r"""
\hline
\end{tabular}

\end{center}
\caption{Event yields for the main processes in the signal region after the BDT selection. The yields are normalized to the results of the fit to the BDT response.}
\label{tab:yields}
\end{table}
""".strip()

def print_proc(pname, t1, e1, t2, e2):
	return "\n"+r"%s & %.1f $\pm$ %.1f  & %.1f $\pm$ %.1f \\" % ( pname, t1, e1, t2, e2)


def parse_line(l):
	samp, tot, err = map(lambda x: x.strip(), l.split("|"))
	return samp, float(tot), float(err)

def hline():
	return "\n" + r"\hline"
if __name__ == "__main__":
	vals = dict()

	inf1 = open(sys.argv[1])
	inf2 = open(sys.argv[2])

	for line1, line2 in zip(inf1.readlines(), inf2.readlines()):
		samp, first_tot, first_err = parse_line(line1)
		samp, second_tot, second_err = parse_line(line2)
		vals[samp.lower()] = first_tot, first_err, second_tot, second_err

	s2 = print_proc(r"\ttbar    " , *vals["ttjets"])
	s2 += print_proc(r"tW        ", *vals["twchan"])
	s2 += print_proc(r"s-channel ", *vals["schan"])
	s2 += hline()

	s2 += print_proc(r"\wjets    ", *vals["wjets"])
	s2 += print_proc(r"\zjets    ", *vals["dyjets"])
	s2 += print_proc(r"Diboson   ", *vals["diboson"])

	s2 += hline()
	s2 += print_proc(r"\QCD      ", *vals["qcd"])
	s2 += hline()

	s2 += print_proc(r"t-channel ", *vals["tchan"])
	s2 += hline()
	s2 += print_proc(r"Total Expected  ", *vals["mc"])
	s2 += hline()
	s2 += "\n" + r"Data       & %.1f  & %.1f \\" % (vals["data"][0], vals["data"][2])

	idstring = r"% BEGIN AUTOGENERATED, NOT FOR CHANGING"
	idstring += "\n" + r"% Generated using plots/yields.py on UTC " + str(datetime.datetime.utcnow())
	idstring += "\n" + r"% Input files " + str([sys.argv[1], sys.argv[2]]) + "\n"
	print idstring + s1+s2+s3 + "\n" + "% END AUTOGENERATED"