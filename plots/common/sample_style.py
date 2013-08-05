from colors import sample_colors_same as sample_colors
from colors import sample_colors_separate
import ROOT
import itertools
from SingleTopPolarization.Analysis import sample_types

class Styling:
    @staticmethod
    def mc_style_nostack(hist, sample_name):
        color = sample_colors[sample_name]
        hist.SetLineColor(color)
        hist.SetLineWidth(4)
        hist.SetMarkerStyle(0)

    @staticmethod
    def mc_style(hist, sample_name):
        color = sample_colors[sample_name]
        hist.SetLineColor(color)
        hist.SetLineWidth(2)
        hist.SetFillColor(color)
        hist.SetFillStyle(1001)

    @staticmethod
    def mc_style_nofill(hist, sample_name):
        color = sample_colors_separate[sample_name]
        hist.SetLineColor(color)
        hist.SetLineWidth(2)        

    @staticmethod
    def data_style(hist):
        hist.SetMarkerStyle(20)
        hist.SetMarkerColor(ROOT.kBlack)
        hist.SetFillStyle(0)

    @staticmethod
    def style_collection(coll):
        for hn, h in coll.hists.items():
            if sample_types.is_mc(hn):
                Styling.mc_style(h, hn)
            else:
                Styling.data_style(h)


class ColorStyleGen:
    col_index = 0
    style_index = 0

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta, ROOT.kYellow+2, ROOT.kBlack, ROOT.kCyan, ROOT.kOrange]
    styles = [1,2,3,4]#, 3005, 3006]

    def __init__(self):
        self.colstyles = itertools.product(self.styles, self.colors)

    def next(self):
        return self.colstyles.next()

    def style_next(self, hist):
        (style, color) = self.next()
        hist.SetFillColor(0)
        hist.SetLineWidth(1)
        hist.SetLineColor(color)
        hist.SetMarkerStyle(0)
        hist.SetFillStyle(0)
        hist.SetLineStyle(style)

    def reset(self):
        self.colstyles = itertools.product(self.colors, self.styles)

    @staticmethod
    def style_hists(hists):
        cg = ColorStyleGen()
        for h in hists:
            cg.style_next(h)
