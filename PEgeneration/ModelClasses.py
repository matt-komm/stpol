import uuid
import numpy
import math

class THETAObject(object):
    def __init__(self, name=""):
        if name=="":
            self.__generateName()
        else:
            self.name=name
        
        self.varname=self.objectType()+"_"+self.name
    
    def __generateName(self):
        self.name=str(uuid.uuid4())
        
    def _indent(self, text, level):
        indention="    "
        str=""
        for cnt in range(level):
            str+=indention
        str+=text
        str+="\n"
        return str
    
    def toConfigString(self, indentLevel=0):
        raise NotImplementedError
    
    def objectType(self):
        raise NotImplementedError

class Model(THETAObject):
    def __init__(self, name="", configDict={}):
        THETAObject.__init__(self, name)
        self._configDict=configDict
        self._observables=[]
        self._parameterDistribution=[]
    
    def addObservable(self, observable):
        self._observables.append(observable)
        for comp in observable.getComponents():
            for dist in comp.getParameterDistributions():
                if dist not in self._parameterDistribution:
                    self._parameterDistribution.append(dist)
                    
    def getParameterNames(self):
        paramsName=""
        for dist in self._parameterDistribution:
            for name in dist.getParameterNames():
                paramsName+="\""+name+"\","
        paramsName=paramsName[:-1]
        return paramsName
        
    def getVariableNames(self):
        paramsVarname=""
        for dist in self._parameterDistribution:
            paramsVarname+="\"@"+dist.getVarName()+"\","
        paramsVarname=paramsVarname[:-1] #remove last comma
        return paramsVarname
    
    def toConfigString(self, indentLevel=0):
        paramsVarname=self.getVariableNames()
        paramsName=self.getParameterNames()
        
        retStr=self._indent(self.varname+" = {", indentLevel)
        for comp in self._observables:
            retStr+=comp.toModelString(indentLevel+1)
        
        retStr+=self._indent("parameter-distribution = {", indentLevel+1)
        retStr+=self._indent("type = \"product_distribution\";", indentLevel+2)
        retStr+=self._indent("distributions = ("+paramsVarname+");", indentLevel+2)
        retStr+=self._indent("};", indentLevel+1)
        
        for config in self._configDict.keys():
            retStr+=self._indent(config+" = "+self._configDict[config]+";", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        
        retStr+=self._indent("parameters = ("+paramsName+");", indentLevel)
        
        retStr+=self._indent("observables = {", indentLevel)
        for observable in self._observables:
            retStr+=observable.toConfigString(indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
    
    def objectType(self):
        return "model"
    
class Observable(THETAObject):
    def __init__(self, name="", binning=1, range=[0.0, 1.0]):
        THETAObject.__init__(self, name)
        self._components=[]
        self._binning=binning
        self._range=range
        
        
    def getComponents(self):
        return self._components
        
    def addComponent(self, component):
        self._components.append(component)
    
    def toConfigString(self, indentLevel=0):
        retStr=self._indent(self.varname+" = {", indentLevel)
        retStr+=self._indent("nbins = "+str(self._binning)+";", indentLevel+1)
        retStr+=self._indent("range = ("+str(self._range[0])+","+str(self._range[1])+");", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
        
    def toModelString(self, indentLevel=0):
        retStr=self._indent(self.varname+" = {", indentLevel)
        for comp in self._components:
            retStr+=comp.toConfigString(indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
    
    def objectType(self):
        return "obs"
    
class ObservableComponent(THETAObject):
    def __init__(self, name=""):
        THETAObject.__init__(self, name)
        self._histograms={}
        self._coefficientFunction=CoefficientMultiplyFunction()
        self._histogramParameterDistributions=[]
        self._parameters=[]
        
    def getParameterDistributions(self):
        list=self._coefficientFunction.getDistributions()+self._histogramParameterDistributions
        return list
        
    def setCoefficientFunction(self, function):
        self._coefficientFunction=function
        
    def setNominalHistogram(self, histogram):
        self._histograms['nominal-histogram']=histogram
    
    def addUncertaintyHistograms(self, histogramUP, histogramDOWN, distribution,parameter=""):
        self._histograms[distribution.getParameterName(parameter)+'-plus-histogram']=histogramUP
        self._histograms[distribution.getParameterName(parameter)+'-minus-histogram']=histogramDOWN
        self._histogramParameterDistributions.append(distribution)
        self._parameters.append(parameter)
        
    def toConfigString(self, indentLevel=0):
        histoParameters=""
        for cnt in range(len(self._histogramParameterDistributions)):
            histoParameters+="\""+self._histogramParameterDistributions[cnt].getParameterName(self._parameters[cnt])+"\","
        histoParameters=histoParameters[:-1] #remove last comma
        
        retStr=self._indent(self.varname+" = {", indentLevel)
        retStr+=self._coefficientFunction.toConfigString(indentLevel+1)
        retStr+=self._indent("histogram = {", indentLevel+1)
        retStr+=self._indent("type = \"cubiclinear_histomorph\";", indentLevel+2)
        retStr+=self._indent("parameters = ("+histoParameters+");", indentLevel+2)
        for histoKey in self._histograms.keys():
            retStr+=self._indent(histoKey+" = \"@"+self._histograms[histoKey].varname+"\";", indentLevel+2)
        retStr+=self._indent("};", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
            
    def objectType(self):
        return "comp"
    
class CoefficientConstantFunction(THETAObject):
    def __init__(self, name="",factor=1.0):
        THETAObject.__init__(self, name)
        self._distributions=[]
        self._factor=factor
        
    def getDistributions(self):
        return []
        
    def toConfigString(self, indentLevel=0):
        return self._indent("coefficient-function = {type = \"multiply\"; factors = ("+str(self._factor)+");};", indentLevel)
    
    def objectType(self):
        return "coefffunction"
    
class CoefficientMultiplyFunction(THETAObject):
    def __init__(self, name=""):
        THETAObject.__init__(self, name)
        self._distributions=[]
        self._parameters=[]
        
    def getDistributions(self):
        return self._distributions
        
    def addDistribution(self, distribution,parameter=""):
        if distribution not in self._distributions:
            self._distributions.append(distribution)
            self._parameters.append(parameter)
        else:
            print "ERROR - Distribution already in CoefficientMultiplyFunction: ", distribution.name
        
    def toConfigString(self, indentLevel=0):
        factors=""
        for cnt in range(len(self._distributions)):
            factors+="\""+self._distributions[cnt].getParameterName(self._parameters[cnt])+"\","
        factors=factors[:-1] #remove last comma
        return self._indent("coefficient-function = {type = \"multiply\"; factors = ("+factors+");};", indentLevel)
    
    def objectType(self):
        return "coefffunction"
    
class Distribution(THETAObject):
    def __init__(self, name="", type="", configDict={}):
        THETAObject.__init__(self, name)
        self._type=type
        self._configDict=configDict
        self.varname=self.varname+"-"+self._type
        
    def setConfigDict(self,configDict):
        self._configDict=configDict
        
    def getParameterName(self,name=""):
        return self.name
    
    def getParameterNames(self):
        return [self.name]
    
    def getVarName(self):
        return self.varname
        
    def toConfigString(self, indentLevel=0):
        retStr=self._indent(self.varname+"={", indentLevel)
        retStr+=self._indent("type=\""+self._type+"\";", indentLevel+1)
        retStr+=self._indent("parameter = \""+self.name+"\";", indentLevel+1)
        for key in self._configDict.keys():
            retStr+=self._indent(key+" = "+self._configDict[key]+";", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
    
    def objectType(self):
        return "dist"

    def __str__(self):
        return self.name+": "+str(self._configDict)
    
class Distribution2D(Distribution):
    def __init__(self, name="",parameterName1="",parameterName2="", type="gauss", configDict={}):
        Distribution.__init__(self, name, type, configDict)
        self.paramName1=parameterName1
        self.paramName2=parameterName2
        
    def setConfigDict(self,configDict):
        self._configDict=configDict
        
    def getParameterName(self,name=""):
        if name=="":
            return self.paramName1
        else:
            if self.paramName1==name:
                return self.paramName1
            elif self.paramName2==name:
                return self.paramName2
            else:
                print "Error - getParameterName failed"
    
    def getParameterNames(self):
        return [self.paramName1,self.paramName2]
    
    def getVarName(self):
        return self.varname
        
    def toConfigString(self, indentLevel=0):
        retStr=self._indent(self.varname+"={", indentLevel)
        retStr+=self._indent("type=\""+self._type+"\";", indentLevel+1)
        retStr+=self._indent("parameters = (\""+self.paramName1+"\", \""+self.paramName2+"\");", indentLevel+1)
        for key in self._configDict.keys():
            retStr+=self._indent(key+" = "+self._configDict[key]+";", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
    
    def objectType(self):
        return "dist"

    def __str__(self):
        return self.name+": "+str(self._configDict)
        
class MultiDistribution(Distribution):
    def __init__(self, name="", type="gauss", configDict={}):
        Distribution.__init__(self, name, type, configDict)
        self.parameters=[]
        self.covariance=numpy.zeros((0,0))
        
    def setConfigDict(self,configDict):
        self._configDict=configDict
    
    def addParameter(self,name,mean=1.0,sigma=0.1):
        self.parameters.append({"name":name,"mean":mean})
        n=len(self.parameters)
        temp=numpy.zeros((n,n))
        for ix in range(n-1):
            for iy in range(n-1):
                temp[ix,iy]=self.covariance[ix][iy]
        self.covariance=temp
        self.covariance[n-1,n-1]=sigma*sigma
        
    def setCovarianceByValue(self,ix,iy,value):
        self.covariance[ix][iy]=value
        self.covariance[iy][ix]=value
        
    def setCovarianceByMatrix(self,matrix):
        if matrix.shape==self.covariance.shape:
            self.covariance=matrix
            
    def setCorrelation(self,name1,name2,rho):
        index1=1000
        index2=1000
        for ix in range(len(self.parameters)):
            if self.parameters[ix]["name"]==name1:
                index1=ix
            if self.parameters[ix]["name"]==name2:
                index2=ix
        print index1,index2
        self.setCovarianceByValue(index1,index2,rho*math.sqrt(self.covariance[index1][index1]*self.covariance[index2][index2]))
        
            
    def getParameterName(self,name):
        for parameter in self.parameters:
            if parameter["name"]==name:
                return name
        print "ERROR while getting the parameter name from a multidimensional distribution"
        
    def getParameterNames(self):
        parameterList=[]
        for parameter in self.parameters:
            parameterList.append(parameter["name"])
        return parameterList
    
    def getVarName(self):
        return self.varname
        
    def toConfigString(self, indentLevel=0):
        retStr=self._indent(self.varname+"={", indentLevel)
        retStr+=self._indent("type=\""+self._type+"\";", indentLevel+1)
        parameterList=""
        meanList=""
        rangeList=""
        for parameter in self.parameters:
            parameterList+="\""+parameter["name"]+"\","
            meanList+=str(parameter["mean"])+","
            rangeList+="(\"-inf\", \"inf\"),"
        retStr+=self._indent("parameters = ("+parameterList[0:-1]+");", indentLevel+1)
        retStr+=self._indent("mean = ["+meanList[0:-1]+"];", indentLevel+1)
        retStr+=self._indent("ranges = ("+rangeList[0:-1]+");", indentLevel+1)
        
        n=len(self.parameters)
        covarianceList=""
        for ix in range(n):
            rowList=""
            for iy in range(n):
                rowList+=""+str(self.covariance[ix][iy])+","
            covarianceList+="["+rowList[0:-1]+"],"
        retStr+=self._indent("covariance = ("+covarianceList[0:-1]+");", indentLevel+1)
        for key in self._configDict.keys():
            retStr+=self._indent(key+" = "+self._configDict[key]+";", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr
    
    def objectType(self):
        return "dist"

    def __str__(self):
        return self.name+": "+str(self._configDict)
    
class RootProjectedHistogram(THETAObject):
    def __init__(self, name="", configDict={}):
        THETAObject.__init__(self, name)
        self._configDict={}
        self._configDict.update(configDict)
        
    def setFileName(self, filename):
        self._configDict['filename']=filename
        
    def setProjectString(self, projectstr):
        self._configDict['projectstr']=projectstr
        
    def setCutString(self, cutstr):
        self._configDict['cutstr']=cutstr
        
    def getCutString(self):
        return self._configDict['cutstr']
        
    def setTupleName(self, tuplename):
        self._configDict['ntuplename']=tuplename
        
    def setBinning(self, binning):
        self._configDict['binning']=binning
        
    def setRange(self, range):
        self._configDict['range']=range
    
    def toConfigString(self, indentLevel=0):
        retStr=self._indent(self.varname+" = {", indentLevel)
        retStr+=self._indent("type = \"root_histogram_from_ntuple\";", indentLevel+1)
        for key in self._configDict.keys():
            if key=="binning":
                retStr+=self._indent(key+" = "+str(self._configDict[key])+";", indentLevel+1)
            elif key=="range":
                retStr+=self._indent(key+" = ("+str(self._configDict[key][0])+","+str(self._configDict[key][1])+");", indentLevel+1)
            elif key=="use_errors":
                retStr+=self._indent(key+" = "+self._configDict[key]+";", indentLevel+1)
            else:
                retStr+=self._indent(key+" = \""+self._configDict[key]+"\";", indentLevel+1)
        retStr+=self._indent("zerobin_fillfactor = 0.0001;", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr

    def objectType(self):
        return "hist"


class RootHistogram(THETAObject):
    def __init__(self, name="", configDict={}):
        THETAObject.__init__(self, name)
        self._configDict={}
        self._configDict.update(configDict)
        
    def setFileName(self, filename):
        self._configDict['filename']=filename
        
    def setHistoName(self, histoname):
        self._configDict['histoname']=histoname
    
    def toConfigString(self, indentLevel=0):
        retStr=self._indent(self.varname+" = {", indentLevel)
        retStr+=self._indent("type = \"root_histogram\";", indentLevel+1)
        for key in self._configDict.keys():
            if key=="zerobin_fillfactor":
                retStr+=self._indent(key+" = "+self._configDict[key]+";", indentLevel+1)
            elif key=="use_errors":
                retStr+=self._indent(key+" = "+self._configDict[key]+";", indentLevel+1)
            else:
                retStr+=self._indent(key+" = \""+self._configDict[key]+"\";", indentLevel+1)
        retStr+=self._indent("zerobin_fillfactor = 0.0001;", indentLevel+1)
        retStr+=self._indent("};", indentLevel)
        return retStr

    def objectType(self):
        return "hist"

