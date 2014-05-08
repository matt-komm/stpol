#!/usr/bin/env python
"""
A module that can draw several histograms side by side with various settings.
"""
__author__ = 'joosep.pata@cern.ch'

import ROOT
ROOT.gROOT.SetBatch(True)
from plots.common.sample import Sample, get_paths
from plots.common.cuts import Cuts
from plots.common.hist_plots import plot_hists_dict
from plots.common.tdrstyle import tdrstyle
from plots.common.utils import merge_hists
from plots.common.histogram import norm
import copy
from os.path import join
import unittest

def compare_plot(plot_def):
    """
    Draws a comparison plot based on a plot definition dictionary, which has the following arguments:
    *mandatory*
        var: a string with the TTree branch name / TFormula expression to plot
        plot_range: the plot range definition for Sample.drawHistogram
        items: a list of tuples, containing the plots to be drawn in the following format
            [
                (name_of_plot, pathname_of_file, filename, cut_object, weight_object)
            ]
    *optional*
        lumi: the luminosity to normalize to in /pb
        merge_cmds: a merge command for the merge_hists method, which merges the histograms
            according to the names in the items list
        hist_callback: a method that is called on each of the histograms after merging,
            having the form:
                def f(hist_name, hist):
                    dostuff
                    return hist
        x_label: a string the the label for the x axis

    *returns*
        a tuple (canvas, final_histogram_dict)

    """
    proc_cuts = plot_def['items']
    var = plot_def.get('var')
    plot_range = plot_def.get('range')
    lumi = plot_def.get('lumi', 20000)
    merge_cmds = plot_def.get('merge_cmds', None)
    hist_callback = plot_def.get('hist_callback', None)
    x_label = plot_def.get('xlab', 'xlab')

    hists = {}
    for name, path, fname, cut, weight in proc_cuts:
        fname = join(path, fname)
        sample = Sample.fromFile(fname)
        hists[name] = sample.drawHistogram(var, str(cut), weight=str(weight), plot_range=plot_range)
        hists[name].SetName(name)
        hists[name] = copy.deepcopy(hists[name])
        hists[name].Scale(sample.lumiScaleFactor(lumi))

    if merge_cmds:
        hists_merged = merge_hists(hists, merge_cmds)
        hists = hists_merged
    if hist_callback:
        for hn, h in hists.items():
            hists[hn] = hist_callback(hn, h)
    canv = plot_hists_dict(hists, x_label=x_label)
    return canv, hists

def fill_list(items):
    """
    Replaces missing elements in a list of tuples.
    The placeholder for a missing element is '-.-' for the copy symbol.
    items: a list of tuples
    returns: a list of tuples where the copy symbols have been replaced with the corresponding element
        from the previous line.
    """
    filled = []
    for item in items:
        item = list(item)
        nsub = len(item)
        for i in range(nsub):
            if item[i]=='-.-':
                item[i] = prev[i]
        prev = item
        filled.append(tuple(item))
    return filled

class TestMethods(unittest.TestCase):
    def test_fill_list(self):
        """
        Do a quick test on the empty element filler method.
        """

        a = [
            ('a', 1),
            ('b', '-.-')
        ]

        b = fill_list(a)
        self.assertEqual(b, 
            [
                ('a', 1),
                ('b', 1)
            ]
        )
### LOOK HERE ###        
##The main plotting method
    def test_plot(self):

        tdrstyle()
        paths = get_paths()
        dataset = 'Jul15'
        lepton = 'mu'
        systematic = 'nominal'
        iso = 'iso'

        #Define the different plots to make
        items = [
            ('tchan1', paths[dataset]['mc'][lepton][systematic][iso], 'T_t_ToLeptons.root', Cuts.n_jets(2), '1.0'),
            ('tbarchan1', '-.-', 'Tbar_t_ToLeptons.root', Cuts.n_jets(2), '1.0'),

            ('tchan2', '-.-', 'T_t_ToLeptons.root', Cuts.n_jets(2)*Cuts.n_tags(1), '1.0'),
            ('tbarchan2', '-.-', 'Tbar_t_ToLeptons.root', Cuts.n_jets(2)*Cuts.n_tags(1), '1.0'),
        ]
        items = fill_list(items)

        #Dewfine a callbakc for normalization
        def normalize(hn, h):
            norm(h)
            return h

        #The final plot definition to draw
        plot_def = {
            'var': 'mt_mu',
            'range': [20, 0, 300],
            'items': items,
            'merge_cmds': {'signal 2J1T':['tchan2', 'tbarchan2'], 'signal 2J':['tchan1', 'tbarchan1']},
            'xlab': 'M_t(W)'
            #'hist_callback': normalize
        }

        #Now do the draw comparison
        canv, hists = compare_plot(plot_def)

        #Do some post-checking that everything went fine
        for hn, h in hists.items():
            if hn=='signal 2J':
                self.assertAlmostEqual(h.Integral(), 39472.452918)
            elif hn=='signal 2J1T':
                self.assertAlmostEqual(h.Integral(), 16414.4804941)

        print "Saving the plot to test_plot.png"
        canv.SaveAs('test_plot.png')


if __name__=='__main__':
    import rootpy
    rootpy.log.basic_config_colorized()
    print 'Running the tests for compare_plot'
    unittest.main()