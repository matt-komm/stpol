from colors import sample_colors_same as sample_colors
from colors import sample_colors_separate
import ROOT
import itertools

class Styling:
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
        hist.SetFillStyle(4001)

class ColorStyleGen:
    col_index = 0
    style_index = 0

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta, ROOT.kYellow, ROOT.kBlack, ROOT.kCyan, ROOT.kOrange]
    styles = [1001]#, 3005, 3006]

    def __init__(self):
        self.colstyles = itertools.product(self.styles, self.colors)

    def next(self):
        return self.colstyles.next()

    def style_next(self, hist):
        (style, color) = self.next()
        hist.SetFillColor(ROOT.kWhite)
        hist.SetLineColor(color)
        hist.SetMarkerStyle(0)
        hist.SetLineStyle(style)

    def reset(self):
        self.colstyles = itertools.product(colors, styles)

    @staticmethod
    def style_hists(hists):
        cg = ColorStyleGen()
        for h in hists:
            cg.style_next(h)
