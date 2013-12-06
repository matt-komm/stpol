import ROOT
from sample_style import Styling

#Need to import ordereddict from python 2.7
try:
    from collections import OrderedDict
except ImportError:
        from odict import OrderedDict

def plot_hists(canv, histos, **kwargs):
    """
    ***Mandatory arguments
    canv - a TCanvas instance to use
    hist_groups - a dictionary with the list of histograms to use as different stacks.
                For example:
                {
                "data": [data_hist],
                "mc:" [mc_hist1, mc_hist2, ...]
                }
                Each key will become a different stack that is compared side-by-side.
                Each list will be inside the stack on top of each other in the order specified.
    ***Optional arguments
    draw_styles - a dictionary with the stack names and the corresponding TH1::Draw styles
    title - plot title (set on the first stack)
    x_label - label of the x axis
    y_label - label of the y axis
    do_log_y - True/False to set log scale on y axis
    min_bin - the lower cutoff on the y axis, which may be necessary for log y scale
    max_bin_mult - the y axis upper limit will be this multipier times the maimal bin height
    ***returns
    a dictionary with the instances of the drawn TStacks.
    """

    #stacks = dict()
    for st in histos.values():
        st.Scale(1/st.Integral())
    draw_styles = kwargs.get("draw_styles", {"data": "E1"})

    do_log_y = kwargs.get("do_log_y", False)

    title = kwargs.get("title", "title")

    x_label = kwargs.get("x_label", "x_label")
    y_label = kwargs.get("y_label", "")

    min_bin = kwargs.get("min_bin", 0)
    max_bin_mult = kwargs.get("max_bin_mult", 1.8)


    """for name, group in hist_groups.items():
        stacks[name] = ROOT.THStack(name, name)
        for hist in group:
            stacks[name].Add(hist)
    """
    max_bin = max([st.GetMaximum() for st in histos.values()])

    #Need to draw the stacks one time to initialize everything
    for name, stack in histos.items():
        stack.Draw()
    canv.Draw()

    #Now draw really
    first = True
    for name, stack in histos.items():
        if name in draw_styles.keys():
            drawcmd = draw_styles[name]
        else:
            Styling.mc_style_nofill(stack, name)
            drawcmd = "HIST E1" #default stack style
        if not first:
            drawcmd += " SAME"
        stack.Draw(drawcmd)

        #Set the plot style on the first stack
        if first:
            stack.SetMaximum(max_bin_mult*max_bin)
            stack.SetMinimum(0)
            if do_log_y:
                stack.SetMinimum(min_bin)
            #stack.SetTitle(title)
            stack.GetXaxis().SetTitle(x_label)
            if len(y_label)>0:
                stack.GetYaxis().SetTitle(y_label)

        first = False
    if do_log_y:
        canv.SetLogy()
    return canv
