import ROOT
from plots.common.sample_style import Styling
#Need to import ordereddict from python 2.7
try:
    from collections import OrderedDict
except ImportError:
    from odict import OrderedDict
import logging
logger = logging.getLogger("stack_plot")
logger.setLevel(logging.INFO)

def plot_hists_stacked(canv, hist_groups, **kwargs):
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
    stack - wether we actually stack or not
    ***returns
    a dictionary with the instances of the drawn TStacks. NB: you must keep the output of this
    method until you print the TCanvas, otherwise the stack references are destroyed.
    """

    logger.debug("plot_hists_stacked: %s %s %s" % (str(canv), str(hist_groups), str(kwargs)))

    stacks = OrderedDict()

    draw_styles = kwargs.get("draw_styles", {"data": "E1"})

    do_log_y = kwargs.get("do_log_y", False)

    title = kwargs.get("title", "title")

    x_label = kwargs.get("x_label", "x_label")
    y_label = kwargs.get("y_label", "")

    min_bin = kwargs.get("min_bin", -1)
    max_bin_mult = kwargs.get("max_bin_mult", 1.8)



    for name, group in hist_groups.items():
        if len(group)==0:
            raise ValueError("Stack group %s was empty" % name)
        stacks[name] = ROOT.THStack(name, name)
        for hist in group:
            stacks[name].Add(hist)

    max_bin = max([st.GetMaximum() for st in stacks.values()])
    logger.info('Maximal bin: %1.3f' % max_bin)
    logger.info('Stack info: %s' % str([(k,v.GetMaximum()) for k,v in stacks.items()]))
    if min_bin == -1:
        min_bin = 0.3*min([st.GetMinimum() for st in stacks.values()])

    do_stack = kwargs.get('stack', True)
    if not do_stack:
        max_bin = max([st.GetMaximum("nostack") for st in stacks.values()])
        min_bin = 0.1*min([st.GetMinimum("nostack") for st in stacks.values()])

    if min_bin == 0:
        if not do_stack:
            min_bin = 0.001
        else: 
            min_bin = 1

    #Need to draw the stacks one time to initialize everything
    for name, stack in stacks.items():
        stack.Draw()
    canv.Draw()
    logger.info("do_stack: %s" % str(do_stack))
    #Now draw really
    first = True
    for name, stack in stacks.items():
        logger.debug("Drawing stack %s" % name)
        if name == 'data' and not do_stack:
            continue
        if name in draw_styles.keys():
            drawcmd = draw_styles[name]
        else:
            drawcmd = "BAR HIST goff" #default stack style

        if not do_stack:
            drawcmd = "nostack hist"
        if not first:
            drawcmd += " SAME"
        logger.info('name: %s drawcmd: %s' % (name,drawcmd))
        logger.info('options: %s' % str(stack.GetOption()))
        stack.Draw(drawcmd)

        #Set the plot style on the first stack
        if first:
            logger.info('minimum: %1.3f maximum: %1.3f' % (min_bin, max_bin_mult*max_bin))
            stack.SetMaximum(max_bin_mult*max_bin)
            if do_log_y:
                stack.SetMinimum(min_bin)
            stack.SetTitle(title)
            stack.GetXaxis().SetTitle(x_label)
            if len(y_label)>0:
                stack.GetYaxis().SetTitle(y_label)

        first = False
    if do_log_y:
        canv.SetLogy()
    canv.Update()
    return stacks


if __name__=="__main__":
    import ROOT
    import random
    import tdrstyle
    logging.basicConfig(level=logging.DEBUG)
    tdrstyle.tdrstyle()

    #Make some test data histograms
    h_d1 = ROOT.TH1F("h_d1", "data1", 20, -5, 5)
    for i in range(1000):
        h_d1.Fill(random.normalvariate(0, 1))

    h_d2 = ROOT.TH1F("h_d2", "data2", 20, -5, 5)
    for i in range(10000):
        h_d2.Fill(random.normalvariate(0, 0.8))

    #Merge the different data samples
    h_d1.Add(h_d2)
    h_d1.SetTitle("data")

    #Make some test MC histograms
    h_mc1 = ROOT.TH1F("h_mc1", "A", 20, -5, 5)
    for i in range(1500):
        h_mc1.Fill(random.normalvariate(0, 1))

    h_mc2 = ROOT.TH1F("h_mc2", "B", 20, -5, 5)
    for i in range(900):
        h_mc2.Fill(random.normalvariate(0, 0.9))

    h_mc3 = ROOT.TH1F("h_mc3", "C", 20, -5, 5)
    for i in range(5000):
        h_mc3.Fill(random.normalvariate(0,  1.2))

    #Set the histogram styles and colors
    from sample_style import Styling
    Styling.mc_style(h_mc1, "TTJets_FullLept")
    Styling.mc_style(h_mc2, "WJets_sherpa")
    Styling.mc_style(h_mc3, "WW")
    Styling.data_style(h_d1)

    #Create the canvas
    canv = ROOT.TCanvas("c", "c")

    #!!!!LOOK HERE!!!!!
    #----
    #Draw the stacked histograms
    #----
    stacks_d = OrderedDict() #<<< need to use OrderedDict to have data drawn last (dict does not preserve order)
    stacks_d["mc"] = [h_mc1, h_mc2, h_mc3] # <<< order is important here, mc1 is bottom-most
    stacks_d["data"] = [h_d1]
    stacks = plot_hists_stacked(
        canv,
        stacks_d,
        x_label="variable x [GeV]",
        y_label="",
        do_log_y=False
    )

    #Draw the legend
    import legend
    leg = legend.legend(
        [h_d1, h_mc3, h_mc2, h_mc1], # <<< need to reverse MC order here
        styles=["p", "f"],
        width=0.2
    )
    canv.Update()
    canv.SaveAs("test.pdf")
    canv.SaveAs("test.png")
