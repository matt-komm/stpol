
import ROOT
import logging

logger = logging.getLogger("legend")
logger.setLevel(logging.WARNING)
def legend(hists, **kwargs):
    """
        ***Mandatory arguments:
        hists - list of TH1* type objects
                The title of the histogram(TH1.GetTitle()) is used as the name in the legend.
                The legend will be in the order of the histograms.
        
        ***Optional arguments:
        names - names of the processes displayed at the legend instead of the histogram titles. Order
                1. data
                2. MC samples in the reverse order to appear in the legend

        legend_pos - a string specifying the desired position on the canvas
        
        width, height - the size of the legend in relative coordinates
        
        styles - an optional list of characters form the set of {p,f} specifying
                whether to draw a filled legend marker (MC) or a point (data)
                If the length of style characters does not equal the length of
                the histogram list, the last character is duplicated to have styles
                for all histograms.
                For example:
                hists=[hist_data, hist_mc1, hist_mc2, hist_mc3]
                styles=["p","f"] becomes styles["p", "f", "f", "f"]
                and the data histogram will be drawn as "p", the mc histogram as "f"
                
        returns - instance of TLegend. You must keep a reference to the instance
                to avoid losing the legend, e.g. you must do
                ...
                h = TH1F(...)
                leg = legend([h], ...) <<< note the leg=..
                ...
                Instead of
                ...
                legend([h], ...)
    """

    #Names of the processes as displayed on a legend
    names = kwargs.get("names")

    pos = kwargs.get("legend_pos", "top-right")
    
    #The relative size of the text in the legend
    text_size = kwargs.get("legend_text_size", 0.03)
    
    nudge_x = kwargs.get("nudge_x", 0.0)
    nudge_y = kwargs.get("nudge_y", 0.0)

    #If you have long names you should make the width larger
    width = kwargs.get("width", 0.21)
    
    #The height is determined automatically with some sensible settings from
    #the number of legend items
    height = kwargs.get("height", text_size*len(hists))

    #The style characters for drawing the legend
    styles = kwargs.get("styles", ["p", "f"])
    
    #Fill the style character array to correct length
    if len(styles)<len(hists):
        styles += [styles[-1]]*(len(hists)-len(styles))
    
    #Check that each histo has a style character
    if len(styles) != len(hists):
        raise ValueError("styles must have the same number of objects as hists")

    #We'll be popping form back, so need to reverse
    styles.reverse()

    #Some 'reasonable' hard-coded positions
    #[bottom_left_x, bottom_left_y, top_right_x, top_right_y]
    #FIXME: fine-tune and make your own
    if pos=="top-right":
        leg_coords = [-1, -1, 0.93, 0.91]
    if pos=="top-left":
        leg_coords = [-1, -1, 0.45, 0.91]

    #Calculate the bottom-left coordinate from top right using the width and height
    if leg_coords[0]==-1:
        leg_coords[0] = leg_coords[2] - width
    if leg_coords[1]==-1:
        leg_coords[1] = leg_coords[3] - height

    leg_coords[0] += nudge_x
    leg_coords[2] += nudge_x
    leg_coords[1] += nudge_y
    leg_coords[3] += nudge_y

    #Expand the array using the wildcard
    leg = ROOT.TLegend(*leg_coords)
    leg.SetFillStyle(0)

    if "names" in kwargs:
        raise Exception("Deprecated stuff. Don't use")
        rnames = names[::-1]
        data = rnames.pop()
        rnames.insert(0,data)
        from odict import OrderedDict
        name_hist_pairs = OrderedDict(zip(rnames, hists))
        
        for name in name_hist_pairs:
            leg_style = styles.pop()
            leg.AddEntry(name_hist_pairs[name],name,leg_style)
        
    else:
        for hist in hists:
            leg_style = styles.pop()
            leg.AddEntry(hist, hist.GetTitle(), leg_style)
            logger.debug("Add legend entry %s: %s" % (hist.GetTitle(), hist))

    leg.Draw()

    leg.SetFillColor(ROOT.kWhite)
    leg.SetLineColor(ROOT.kWhite)
    leg.SetTextSize(text_size)

    #Need to return the legend to keep a reference
    return leg

if __name__=="__main__":
    #Load the tdrstyle
    import tdrstyle
    tdrstyle.tdrstyle()
    
    #make a test canvas
    import ROOT
    canv = ROOT.TCanvas()
    canv.SetCanvasSize(500,500)
    canv.SetWindowSize(int(1.2*500),int(1.2*500))

    #Create some test histograms
    h1 = ROOT.TH1F("h1", "histo 1", 20, -5, 5)
    h2 = ROOT.TH1F("h2", "histo 2", 20, -5, 5)
    import random
    for i in range(10000):
        h1.Fill(random.normalvariate(0, 1))
        h2.Fill(random.normalvariate(0, 2))

    #Draw the hists
    h1.Draw("E") 
    h1.SetFillColor(ROOT.kBlue) #make the legend box filled
    h1.SetStats(False)
    h2.SetLineColor(ROOT.kRed)
    h2.SetFillColor(ROOT.kRed)
    h2.Draw("SAME H")

    #---------
    #Make the legend
    #---------
    leg = legend([h1, h2], pos="top-left", styles=["p", "f"])

    #If you want to change the plot title you've got to change
    #the title of the histogram drawn first, after making the legend
    h1.SetTitle("plot")
