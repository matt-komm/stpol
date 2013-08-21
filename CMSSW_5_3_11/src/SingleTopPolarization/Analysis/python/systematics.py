import numpy as np
import math
import logging
logger = logging.getLogger("systematics")
logger.setLevel(logging.DEBUG)

def to_arr(x):
    """
    Converts an iterable to a numpy array
    """
    return np.array(list(x))

def quadsum(*args):
    """
    Calculates the sqrt of the quadratic sum of a list of variables.
    """
    pow2 = map(lambda x: np.power(x, 2), args)
    sum2 = reduce(lambda x,y: x+y, pow2)
    ret = np.sqrt(sum2)
    return ret

def n_events(hist):
    """
    Under the assumption of Poisson errors, gets the per-bin array
    of the number of MC events that entered a particular histogram
    """
    errs = to_arr(hist.errors())
    n = np.power(errs, 2)
    return n

def cdf_errors(hist, sign=+1):
    """
    Implements the statistical errors a la CDF for a histogram with
    low event counts. 
    """
    hc = hist.Clone()
    n = n_events(hc)
    for i in range(hc.nbins()):
        hc.SetBinError(i+1,
            sign*0.5 + math.sqrt(
                n[i] + 0.25
            )
        )
    return hc

def total_syst(nominal, systs, **kwargs):
    """
    Given a nominal histogram and a list of up/down variations
    corresponding to systematics, calculate the total up/down
    variation assuming uncorrelated errors across systematics
    bins.
    Additionally, the stat. + syst. error band is calculated,
    assuming uncorrelated errors.

    Args:
        nominal: the unvaried Histogram instance corresponding
            to the model
        systs: a list of tuples (name, (hist_up, hist_down))
            corresponding to a systematic variation.

    Keywords:
        consider_variated_stat_err:
            since the variated templates are also derived from
            limited statistics, one must, in principle,
            consider their means as a random variable drawn
            from a distribution.
            0: don't consider the statistical error
            1: consider it and add in quadrature, which has no
                strong statistical basis
            -1: consider it and subtract in quadrature, which
                takes into account the fact that the variation
                is more likely to be in the direction of the nominal
                than the opposite. See http://arxiv.org/pdf/hep-ex/0207026v1.pdf
        symmetric: symmetrize the systematic errors, using a
            Gaussian with mean=nominal and sigma=up-down.
            Otherwise, a two-sided gaussian is assumed, with
            mean=nominal, sigma1=up-nominal, sigma2=nominal-down,
            and addition is performed via convolution
    Returns:
        a 4-tuple of histograms corresponding to the total uncorrelated
        systematic up/down variation and the uncorrelated
        systematic + statistical variation. 
    """
    if isinstance(systs, dict):
        systs = systs.items()

    cdf_nom_up = cdf_errors(nominal, +1)
    cdf_nom_down = cdf_errors(nominal, -1)

    bins = to_arr(nominal.y())

    for systn, (hup, hdown) in systs:
        cdf_errors(hup, sign=+1)
        cdf_errors(hdown, sign=-1)

    #Add the statistical uncertainty
    systs.append(
        ("stat",
            (
                bins + to_arr(cdf_nom_up.errors()),
                bins - to_arr(cdf_nom_down.errors())
            )
        )
    )

    from util.stats.asym_errs import add_errors
    delta_up = np.empty_like(bins)
    delta_down = np.empty_like(bins)

    def add_naive(sigmas):
        sig1 = math.sqrt(sum([s[0]**2 for s in sigmas]))
        sig2 = math.sqrt(sum([s[1]**2 for s in sigmas]))
        #import pdb; pdb.set_trace()
        return sig1, sig2, 0

    #Add systematic variations bin-by-bin
    for i in range(len(bins)):
        sigmas = []
        names = []
        for systn, (hup, hdown) in systs:
            sigma_plus = abs(hup[i] - bins[i])
            sigma_minus = abs(hdown[i] - bins[i])
            sigmas.append(
                (sigma_plus, sigma_minus)
            )
            names.append(systn)
        sig_up, sig_down, delta = add_naive(sigmas)
        
        sumsq = lambda n: math.sqrt(
            sum(map(
            lambda x: x**2,
            map(lambda z: z[n], sigmas)
        )))
        sig_up_naive = sumsq(0)
        sig_down_naive = sumsq(1)

        logger.debug(
            "y=%.2f sig_up=%.2f, sig_down=%.2f, delta=%.2f, sig_up_naive=%.2f, sig_down_naive=%.2f \nsigmas=%s" %
            (bins[i], sig_up, sig_down, delta, sig_up_naive, sig_down_naive, str(zip(names, sigmas)))
        )

        delta_up[i] = sig_up
        delta_down[i] = sig_down

    bins_up = bins + delta_up
    bins_down = bins - delta_down

    hup_syst_stat = nominal.Clone()
    hdown_syst_stat = nominal.Clone()
    for i in range(len(bins)):
        hup_syst_stat.SetBinContent(i+1, bins_up[i])
        hdown_syst_stat.SetBinContent(i+1, bins_down[i])
        hup_syst_stat.SetBinError(i+1, 0)
        hdown_syst_stat.SetBinError(i+1, 0)

    return hup_syst_stat, hdown_syst_stat


import unittest
from rootpy.plotting import Hist
class TestErrors(unittest.TestCase):

    @staticmethod
    def print_hist(h):
        errs = list(h.errors())
        x = list(h.x())
        for i in range(h.nbins()):
            print "%d | %.2f | %.2f | %.2f" % (i, x[i], h[i], errs[i])

    @staticmethod
    def make_hist(n=5):
        hi = Hist(n, -1, 1)
        hi.Sumw2()
        for i in range(hi.nbins()):
            hi[i] = i
            hi.SetBinError(i+1, math.sqrt(hi[i]))
        return hi

    @staticmethod
    def variate_hist(h, coef=lambda n: 1):
        h = h.Clone()
        errs = list(h.errors())
        for i in range(h.nbins()):
            h.SetBinContent(i+1, h[i] + coef(i) * errs[i])
        return h

    def test_systematic(self):
        hi = self.make_hist()
        hi_up = self.variate_hist(hi)
        self.print_hist(hi)
        self.print_hist(hi_up)

    def test_cdf_errors(self):
        hi = Hist(list(range(20)))
        hi.Sumw2()
        for i in range(1, hi.nbins()+1):
            hi.SetBinContent(i, i-1)
            hi.SetBinError(i, math.sqrt(hi[i-1]))
        self.print_hist(hi)
        hi_up = cdf_errors(hi, +1)
        hi_down = cdf_errors(hi, -1)
        print "up"
        self.print_hist(hi_up)
        print "down"
        self.print_hist(hi_down)

if __name__=="__main__":
    unittest.main()