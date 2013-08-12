import numpy

def total_syst(nominal, systs):
    """
    Given a nominal histogram and a list of up/down variations
    corresponding to systematics, calculate the total up/down
    variation assuming uncorrelated errors across systematics
    bins.

    Args:
        nominal: the unvaried Histogram instance corresponding
            to the model
        systs: a list of tuples (name, (hist_up, hist_down))
            corresponding to a systematic variation.
    Returns:
        a pair of histograms corresponding to the total uncorrelated
        up/down variation. 
    """
    if isinstance(systs, dict):
        systs = systs.items()
    bins = numpy.array(list(nominal.y()))

    diff_up_tot = numpy.zeros(bins.shape)
    diff_down_tot = numpy.zeros(bins.shape)
    for systn, (hup, hdown) in systs:
        bins_up = numpy.array(list(hup.y()))
        bins_down = numpy.array(list(hdown.y()))
        diff_up = bins - bins_up
        diff_down = bins - bins_down
        diff_up_tot += numpy.power(diff_up, 2)
        diff_down_tot += numpy.power(diff_down, 2)

    diff_up_tot = numpy.sqrt(diff_up_tot)
    diff_down_tot = numpy.sqrt(diff_down_tot)

    hup = nominal.Clone("syst_up")
    hdown = nominal.Clone("syst_down")

    bins_up = bins + diff_up_tot
    bins_down = bins - diff_down_tot

    for i in range(len(bins)):
        hup.SetBinContent(i+1, bins_up[i])
        hdown.SetBinContent(i+1, bins_down[i])

    return hup, hdown
