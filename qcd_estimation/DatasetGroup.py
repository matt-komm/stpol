from Dataset import *

class DatasetGroup:
   def __init__(self, name, color, isMC=True, lineStyle=1, title=""):
      self._name=name
      self._color=color
      self._isMC=isMC
      self._datasets=[]
      self._histograms={}
      self._lineStyle=lineStyle
      self._title=title

   def __len__(self):
      return len(self._datasets)

   def add(self, datasets):
      if isinstance(datasets,Dataset):
         self._datasets.append(datasets)
      else:
         self._datasets.extend(datasets)

   def getColor(self):
      return self._color

   def getFillColor(self):
      return self._color
   
   def getName(self):
      return self._name

   def getTitle(self):
      return self._title   

   def setTitle(self, title):
      self._title = title  

   def getDatasets(self):
      return self._datasets

   def addHistogram(self, histo, var, syst="", iso="Iso", extra=""):
      histo.SetLineColor(self._color)
      histo.SetLineStyle(self._lineStyle)
      self._histograms[var.name + syst + iso + extra] = histo
      
   def getHistogram(self, var, syst="", iso="Iso", extra=""):
      return self._histograms[var.name + syst + iso +extra]

   def cleanHistograms(self):
      self._histograms = {}   

   def addHistogram2D(self, histo, var1, var2, label=""):
      self._histograms[var1.name + var2.name + label] = histo

   def getHistogram2D(self, var1, var2, label=""):
      return self._histograms[var1.name + var2.name + label]

   def isMC(self):
      return self._isMC

   def setQCDHisto(self, histo, var, label=""):
      self.addHistogram(histo, var, label+"QCD")
      
   def getQCDHisto(self, var, label=""):
      return self.getHistogram(var, label+"QCD")
