import numpy as np
import math
import logging
logger = logging.getLogger("systematics")
logger.setLevel(logging.DEBUG)
def to_arr(x):
    return np.array(list(x))

def quadsum(*args):
    pow2 = map(lambda x: np.power(x, 2), args)
    sum2 = reduce(lambda x,y: x+y, pow2)
    ret = np.sqrt(sum2)
    return ret

def n_events(hist):
    errs = to_arr(hist.errors())
    n = np.power(errs, 2)
    return n

def cdf_errors(hist, sign=+1):
    n = n_events(hist)
    #logger.info("Errs: %s" % str(to_arr(hist.errors())))
    for i in range(hist.nbins()):
        hist.SetBinError(i+1,
            sign*0.5*math.sqrt(
                n[i] + 0.25
            )
        )

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
        symmetric: symmetrize the systematic errors, using a
            Gaussian with mean=nominal and sigma=up-down.
            Otherwise, a two-sided gaussian is assumed, with
            mean=nominal, sigma1=up-nominal, sigma2=nominal-down.
    Returns:
        a 4-tuple of histograms corresponding to the total uncorrelated
        systematic up/down variation and the uncorrelated
        systematic + statistical variation. 
    """
    if isinstance(systs, dict):
        systs = systs.items()

    consider_variated_stat_err = kwargs.get("consider_variated_stat_err", True)

    if consider_variated_stat_err:
        consider_variated_stat_err = 1.0
    else:
        consider_variated_stat_err = 0.0
        logger.debug(
            """Not taking into account the
            statistical error in the variated templates"""
        )
    symmetric = kwargs.get("symmetric", True)

    bins = to_arr(nominal.y())
    errs = to_arr(nominal.errors())

    #The total difference resulting from the systematic variation
    diff_up_tot = np.zeros(bins.shape)
    diff_down_tot = np.zeros(bins.shape)

    diff_tot = np.zeros(bins.shape)
    # Consider each systematic variation separately, assuming
    # no correlations
    for systn, (hup, hdown) in systs:

        cdf_errors(hup, sign=+1)
        cdf_errors(hdown, sign=-1)

        # The variated templates
        bins_up = to_arr(hup.y())
        bins_down = to_arr(hdown.y())

        # The difference between the nominal and the variated shape, taking into account
        # the lack of information about the central value of the variated shapes from low statistics.
        diff_up = quadsum(bins - bins_up,
            float(consider_variated_stat_err)*to_arr(hup.errors())
        )
        diff_down = quadsum(bins - bins_down,
            float(consider_variated_stat_err)*to_arr(hdown.errors())
        )
        diff = quadsum(bins_up - bins_down,
            float(consider_variated_stat_err)*to_arr(hdown.errors()),
            float(consider_variated_stat_err)*to_arr(hup.errors())
        )

        diff_up_tot += np.power(diff_up, 2)
        diff_down_tot += np.power(diff_down, 2)
        diff_tot += np.power(diff, 2)

    diff_up_tot = np.sqrt(diff_up_tot)
    diff_down_tot = np.sqrt(diff_down_tot)
    diff_tot = np.sqrt(diff_tot)

    #Systematic variation only
    hup = nominal.Clone("syst_up")
    hdown = nominal.Clone("syst_down")
    if symmetric:
        bins_up = bins + diff_tot
        bins_down = bins - diff_tot
    else:
        bins_up = bins + diff_up_tot
        bins_down = bins - diff_down_tot

    for i in range(len(bins)):
        hup.SetBinContent(i+1, bins_up[i])
        hdown.SetBinContent(i+1, bins_down[i])

    #Statistical plus systematic, assuming uncorrelated
    hup_syst_stat = nominal.Clone("syst_stat_up")
    hdown_syst_stat = nominal.Clone("syst_stat_down")
    delta_up = quadsum(diff_up_tot, errs)
    delta_down = quadsum(diff_down_tot, errs)
    delta = quadsum(diff_tot, errs)

    if symmetric:
        bins_up = bins + delta
        bins_down = bins - delta
    else:
        bins_up = bins + delta_up
        bins_down = bins - delta_down

    for i in range(len(bins)):
        hup_syst_stat.SetBinContent(i+1, bins_up[i])
        hdown_syst_stat.SetBinContent(i+1, bins_down[i])


    return hup, hdown, hup_syst_stat, hdown_syst_stat
