import os
import sys
import numpy
import math
import ROOT
import random
import json
import argparse
import scipy
import ctypes
import scipy.interpolate

# ROOT.gStyle.SetHistFillStyle(0)
# ROOT.gStyle.SetLegoInnerR(Float_t rad = 0.5)
# ROOT.gStyle.SetNumberContours(Int_t number = 20)
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetOptDate(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFile(0)
ROOT.gStyle.SetOptTitle(0)

ROOT.gStyle.SetCanvasBorderMode(0)
ROOT.gStyle.SetCanvasColor(ROOT.kWhite)

ROOT.gStyle.SetPadBorderMode(0)
ROOT.gStyle.SetPadColor(ROOT.kWhite)
ROOT.gStyle.SetGridColor(ROOT.kBlack)
ROOT.gStyle.SetGridStyle(2)
ROOT.gStyle.SetGridWidth(1)

ROOT.gStyle.SetFrameBorderMode(0)
ROOT.gStyle.SetFrameBorderSize(0)
ROOT.gStyle.SetFrameFillColor(0)
ROOT.gStyle.SetFrameFillStyle(0)
ROOT.gStyle.SetFrameLineColor(1)
ROOT.gStyle.SetFrameLineStyle(1)
ROOT.gStyle.SetFrameLineWidth(0)

ROOT.gStyle.SetEndErrorSize(2)
ROOT.gStyle.SetErrorX(0.)
ROOT.gStyle.SetMarkerStyle(20)

ROOT.gStyle.SetHatchesSpacing(0.9)
ROOT.gStyle.SetHatchesLineWidth(2)

ROOT.gStyle.SetTitleColor(1, "XYZ")
ROOT.gStyle.SetTitleFont(43, "XYZ")
ROOT.gStyle.SetTitleSize(33, "XYZ")
ROOT.gStyle.SetTitleXOffset(1.135)
ROOT.gStyle.SetTitleOffset(1.32, "YZ")

ROOT.gStyle.SetLabelColor(1, "XYZ")
ROOT.gStyle.SetLabelFont(43, "XYZ")
ROOT.gStyle.SetLabelSize(29, "XYZ")
ROOT.gStyle.SetLabelOffset(0.012, "XY")

ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetStripDecimals(True)
ROOT.gStyle.SetNdivisions(1005, "X")
ROOT.gStyle.SetNdivisions(506, "Y")

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPaperSize(8.0*1.35,6.7*1.35)
ROOT.TGaxis.SetMaxDigits(3)
ROOT.gStyle.SetLineScalePS(2)


ROOT.gStyle.SetPaintTextFormat("3.0f")
ROOT.gStyle.SetLineStyleString(12,"7 6");

colors = []
    
def newColorRGB(red,green,blue):
    newColorRGB.colorindex+=1
    color=ROOT.TColor(newColorRGB.colorindex,red,green,blue)
    colors.append(color)
    return color
    
def HLS2RGB(hue,light,sat):
    r, g, b = ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
    ROOT.TColor.HLS2RGB(
        int(round(hue*255.)),
        int(round(light*255.)),
        int(round(sat*255.)),
        r,g,b
    )
    return r.value/255.,g.value/255.,b.value/255.
    
def newColorHLS(hue,light,sat):
    r,g,b = HLS2RGB(hue,light,sat)
    return newColorRGB(r,g,b)
    
newColorRGB.colorindex=301
'''
colorList = [
    [0.,newColorHLS(0.6, 0.47,0.6)],
    [0.,newColorHLS(0.56, 0.65, 0.7)],
    [0.,newColorHLS(0.52, 1., 1.)],
]
'''
colorList = [
    [0.,newColorHLS(0.8, 0.6,0.95)],
    [0.,newColorHLS(0.7, 0.61,0.95)],
    [0.,newColorHLS(0.6, 0.63,0.95)],
    [0.,newColorHLS(0.4, 0.65,0.9)],
    [0.,newColorHLS(0.15, 0.68,0.9)],
    [0.,newColorHLS(0.0, 0.72,0.9)],
]


lumiMin = min(map(lambda x:x[1].GetLight(),colorList))
lumiMax = max(map(lambda x:x[1].GetLight(),colorList))

for color in colorList:
    color[0] = ((color[1].GetLight()-lumiMin)/(lumiMax-lumiMin))

stops = numpy.array(map(lambda x:x[0],colorList))
red   = numpy.array(map(lambda x:x[1].GetRed(),colorList))
green = numpy.array(map(lambda x:x[1].GetGreen(),colorList))
blue  = numpy.array(map(lambda x:x[1].GetBlue(),colorList))

start=ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 200)
ROOT.gStyle.SetNumberContours(200)
    
    
ptSymbol = "p#kern[-0.8]{ }#lower[0.3]{#scale[0.7]{T}}"
metSymbol = ptSymbol+"#kern[-2.3]{ }#lower[-0.8]{#scale[0.7]{miss}}"
metSymbol_lc = ptSymbol+"#kern[-2.3]{ }#lower[-0.8]{#scale[0.7]{miss,#kern[-0.5]{ }#mu-corr.}}}"
minDPhiSymbol = "#Delta#phi#lower[-0.05]{*}#kern[-1.9]{ }#lower[0.3]{#scale[0.7]{min}}"
htSymbol = "H#kern[-0.7]{ }#lower[0.3]{#scale[0.7]{T}}"
mhtSymbol = "H#kern[-0.7]{ }#lower[0.3]{#scale[0.7]{T}}#kern[-2.2]{ }#lower[-0.8]{#scale[0.7]{miss}}"
rSymbol = mhtSymbol+"#lower[0.05]{#scale[1.2]{/}}"+metSymbol
rSymbol_lc = mhtSymbol+"#lower[0.05]{#scale[1.2]{/}}"+metSymbol_lc
mzSymbol = "m#lower[0.3]{#scale[0.7]{#mu#mu}}"
gSymbol = "#tilde{g}"
qbarSymbol = "q#lower[-0.8]{#kern[-0.89]{#minus}}"
mgSymbol = "m#lower[0.2]{#scale[0.8]{#kern[-0.75]{ }"+gSymbol+"}}"
chiSymbol = "#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}"
mchiSymbol = "m#lower[0.2]{#scale[0.8]{"+chiSymbol+"}}"
    

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i', dest='input', type=str, help='Input folder',required=True)
args = parser.parse_args()
    
basePath = args.input
    



with open('eventyields.json',) as f:
    genweights = json.load(f)

ctauValues = ["0p01","0p1","1","10","100","1000","10000"]
#ctauValues = ["0p1","1","10","100","1000","10000"]
#ctauValues = ["10"]
ctauLabels = {
    #"0p001":"1#kern[-0.2]{ }#mum",
    "0p01":"10#kern[-0.2]{ }#mum",
    "0p1":"100#kern[-0.2]{ }#mum",
    "1":"1#kern[-0.2]{ }mm",
    "10":"10#kern[-0.2]{ }mm",
    "100":"100#kern[-0.2]{ }mm",
    "1000":"1#kern[-0.2]{ }m",
    "10000":"10#kern[-0.2]{ }m",
}
ctauValueMap = {
    #"0p001":0,
    "0p01":0,
    "0p1":1,
    "1":2,
    "10":3,
    "100":4,
    "1000":5,
    "10000":6,
}

massesDict = {}
for ctau in ctauValues:
    ctauSampleName = "SMS-T1qqqq_ctau-%s_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"%ctau
    if not massesDict.has_key(ctau):
        massesDict[ctau] = {}
    for signalSample in [ctauSampleName,ctauSampleName+"_extra"]:
        for llpMass in genweights[signalSample].keys():
            for lspMass in genweights[signalSample][llpMass].keys():
                if genweights[signalSample][llpMass][lspMass]["sum"]<10:
                    continue
                if int(llpMass)==int(lspMass):
                    continue
                if not massesDict[ctau].has_key(llpMass):
                    massesDict[ctau][llpMass] = []
                if not lspMass in massesDict[ctau][llpMass]:
                    massesDict[ctau][llpMass].append(lspMass)

def getTheoryXsecFct(filePath):
    f = open(filePath)
    llpvalues = []
    xsecvalues = []
    xsecvaluesUp = []
    xsecvaluesDown = []
    for l in f:
        if len(l)==0:
            continue
        splitted = l.split(",")
        if len(splitted)!=3:
            print "cannot parse xsec line: ",l
            continue
        llpvalues.append(float(splitted[0]))
        xsec = float(splitted[1])
        xsecRelUnc = float(splitted[2])
        xsecvalues.append(math.log(xsec))
        xsecvaluesUp.append(math.log(xsec*(1+xsecRelUnc)))
        xsecvaluesDown.append(math.log(xsec*(1-xsecRelUnc)))
        
    llpvalues = numpy.array(llpvalues,dtype=numpy.float32)
    xsecvalues = numpy.array(xsecvalues,dtype=numpy.float32)
    xsecvaluesUp = numpy.array(xsecvaluesUp,dtype=numpy.float32)
    xsecvaluesDown = numpy.array(xsecvaluesDown,dtype=numpy.float32)
    
    tckXsec = scipy.interpolate.splrep(llpvalues,xsecvalues,s=1e-3)
    tckXsecUp = scipy.interpolate.splrep(llpvalues,xsecvaluesUp,s=1e-3)
    tckXsecDown = scipy.interpolate.splrep(llpvalues,xsecvaluesDown,s=1e-3)

    def getValue(llpMass):
        xsec = math.exp(scipy.interpolate.splev(llpMass,tckXsec))
        xsecUp = math.exp(scipy.interpolate.splev(llpMass,tckXsecUp))
        xsecDown = math.exp(scipy.interpolate.splev(llpMass,tckXsecDown))
        return xsec,xsecUp,xsecDown
    return getValue
    
    
def interpolatedHist(limitFct,binningX,binningY):
    newHist = ROOT.TH2F(
        "interpolated"+str(random.random()),
        "",
        len(binningX)-1,
        binningX,
        len(binningY)-1,
        binningY
    )
    newHist.SetDirectory(0)
    
    for ibin in range(newHist.GetNbinsX()):
        llpMass = newHist.GetXaxis().GetBinCenter(ibin+1)*1000
        for jbin in range(newHist.GetNbinsY()):
            lspMass = newHist.GetYaxis().GetBinCenter(jbin+1)*1000
            if (llpMass-lspMass)<100:
                continue
            newHist.SetBinContent(ibin+1,jbin+1,limitFct(llpMass,lspMass))
    
    return newHist 

def interpolatedLimitFct(result,kind="median"):
    xvalues = []
    yvalues = []
    zvalues = []
    for llpMass in sorted(result.keys()):
        for lspMass in sorted(result[llpMass].keys()):
            loglimit = math.log(result[llpMass][lspMass][kind])
            xvalues.append(int(llpMass))
            yvalues.append(math.sqrt(100+int(llpMass)-int(lspMass)))
            zvalues.append(loglimit)
    xvalues = numpy.array(xvalues,dtype=numpy.float32)
    yvalues = numpy.array(yvalues,dtype=numpy.float32)
    zvalues = numpy.array(zvalues,dtype=numpy.float32)
   
    tck = scipy.interpolate.bisplrep(
        xvalues,
        yvalues,
        zvalues,
        kx=3,
        ky=3,
        s=1e-3
    )
       
    def getValue(llpMass,lspMass):
        tckCopy = numpy.copy(tck)
        return numpy.exp(scipy.interpolate.bisplev(
            1.*int(llpMass),1.*math.sqrt(100+int(llpMass)-int(lspMass)),tckCopy
        ))
        
    n = 0
    meanDiff = 0.
    meanDiff2 = 0.
    maxDiff = 0.
    for llpMass in sorted(result.keys()):
        for lspMass in sorted(result[llpMass].keys()):
            n+=1
            limit = (result[llpMass][lspMass][kind])
            limitSmooth = getValue(1.*int(llpMass),1.*int(lspMass))
            diff = 1-limitSmooth/limit
            meanDiff += math.fabs(diff)
            meanDiff2 += math.fabs(diff)**2
            maxDiff = max(maxDiff, math.fabs(diff))
    print "rel. interpolation difference mean: %5.3f+-%.3f (max: %5.3f)"%(meanDiff/n,math.sqrt(meanDiff2/n-(meanDiff/n)**2),maxDiff)
 
        
    return getValue
    
def interpolatedLimitFct2(result,kind="median"):
    xvalues = []
    yvalues = []
    zvalues = []
    for llpMass in sorted(result.keys()):
        for lspMass in sorted(result[llpMass].keys()):
            loglimit = math.log(result[llpMass][lspMass][kind])
            xvalues.append(int(llpMass))
            yvalues.append((100+int(llpMass)-int(lspMass)))
            zvalues.append(loglimit)
    xvalues = numpy.array(xvalues,dtype=numpy.float32)
    yvalues = numpy.array(yvalues,dtype=numpy.float32)
    zvalues = numpy.array(zvalues,dtype=numpy.float32)
   
       
    def getValue(llpMass,lspMass):
        xval = 1.*int(llpMass)
        yval = (100+int(llpMass)-int(lspMass))
        
        distances = numpy.zeros(len(xvalues))
        values = numpy.zeros(len(xvalues))
        
        for i in range(len(xvalues)):
            distance = math.sqrt((xvalues[i]-xval)**2+(yvalues[i]-yval)**2)
            distances[i] = distance
            values[i] = zvalues[i]
        
        sortedIndices = numpy.argsort(distances)
        distances = distances[sortedIndices]
        values = values[sortedIndices]
        #print distances
        #print values
        wsum = 0.
        vsum = 0.
        
        wsumExclNearest = 0.
        vsumExclNearest = 0.
        
        for i in range(len(distances)):
            weight = math.exp(-distances[i]**1.7/((20+numpy.mean(distances[0:2]))**1.7))
            vsum += weight*values[i]
            wsum+=weight
            
            if i>=1:
                weightExclNearest = math.exp(-distances[i]**1.7/((20+numpy.mean(distances[1:2]))**1.7))
                wsumExclNearest += weightExclNearest*values[i]
                vsumExclNearest+=weightExclNearest
                
                
        result = math.exp(vsum/wsum)
        #resultExclNearest = math.exp(vsumExclNearest/wsumExclNearest)
        
        
        return result#(distances[1]*resultExclNearest+distances[0]*result)/(distances[1]+distances[0])
        
        '''
        nearestX = (numpy.abs(xvalues[1:-1]-xval)).argmin()+1
        nearestY = (numpy.abs(yvalues[1:-1]-yval)).argmin()+1
        
        
            
        if xvalues[nearestX]>xval:
            leftX = xvalues[nearestX-1]
            rightX = xvalues[nearestX]
            zleftX = zvalues[nearestX-1]
            zrightX = zvalues[nearestX]
        else:
            leftX = xvalues[nearestX]
            rightX = xvalues[nearestX+1]
            zleftX = zvalues[nearestX]
            zrightX = zvalues[nearestX+1]
            
        if yvalues[nearestY]>yval:
            leftY = yvalues[nearestY-1]
            rightY = yvalues[nearestY]
            zleftY = zvalues[nearestY-1]
            zrightY = zvalues[nearestY]
        else:
            leftY = yvalues[nearestY]
            rightY = yvalues[nearestY+1]
            zleftY = zvalues[nearestY]
            zrightY = zvalues[nearestY+1]
        
        xfrac = (xval-leftX)/(rightX-leftX)
        yfrac = (yval-leftY)/(rightY-leftY)
        
        print yval,leftY,rightY
        
        return 0.5*(xfrac*zleftX+(1-xfrac)*zrightX+zleftY*yfrac+(1-yfrac)*zrightY)
        '''
        
    n = 0
    meanDiff = 0.
    meanDiff2 = 0.
    maxDiff = 0.
    for llpMass in sorted(result.keys()):
        for lspMass in sorted(result[llpMass].keys()):
            n+=1
            limit = (result[llpMass][lspMass][kind])
            limitSmooth = getValue(1.*int(llpMass),1.*int(lspMass))
            diff = 1-limitSmooth/limit
            meanDiff += math.fabs(diff)
            meanDiff2 += math.fabs(diff)**2
            maxDiff = max(maxDiff, math.fabs(diff))
    print "rel. interpolation difference mean: %5.3f+-%.3f (max: %5.3f)"%(meanDiff/n,math.sqrt(meanDiff2/n-(meanDiff/n)**2),maxDiff)
 
        
    return getValue
    
    
def parseCombineJson(filePath):
    if not os.path.exists(filePath):
        return None    
    data = json.load(open(filePath))
    mapping = {
        "median": "exp0", 
        "+1":"exp+1", 
        "-1":"exp-1",
        "+2":"exp+2",
        "-2":"exp-2"
    }
    result = {}
    for k,v in mapping.iteritems():
        if not data.has_key("120.0"):
            return None
        if data["120.0"].has_key(v):
            result[k]=data["120.0"][v]
        
    return result

def parseCombineResult(filePath):
    rootFile = ROOT.TFile(filePath)
    limitTree = rootFile.Get("limit")
    result = {}
    #note: combine seems to be not very precise here
    mapping = {
        "median": 0.5, 
        "+1":0.840, 
        "-1":0.160,
        "+2":0.975,
        "-2":0.025
    }
    for entry in range(limitTree.GetEntries()):
        limitTree.GetEntry(entry)
        found = False
        for k,v in mapping.iteritems():
            if math.fabs(limitTree.quantileExpected-v)<0.0001:
                result[k] = limitTree.limit
                found = True
                break
        if not found and limitTree.quantileExpected>0:
            print "unknown quantile: ",limitTree.quantileExpected

    return result


results = {}



for ctau in ctauValues:
    results[ctau] = {}
    for llpMass in sorted(massesDict[ctau].keys()):
        results[ctau][llpMass] = {}
        for lspMass in massesDict[ctau][llpMass]:
            signalProcess = "ctau%s_llp%s_lsp%s"%(ctau,llpMass,lspMass)
            combineJsonFile = os.path.join(basePath,"limits_%s.json"%signalProcess)
            result = parseCombineJson(combineJsonFile)
            if not result:
                print "ERROR: file '"+combineJsonFile+"' not found -> skip"
                continue
            if len(result.keys())!=5:
                print "WARNING: Not all quantiles found in file ",combineJsonFile
            if not result.has_key("median"):
                print "ERROR: Median found in file ",combineJsonFile," -> skip"
                continue
            results[ctau][llpMass][lspMass] = result
                
   
limitsU = {}
limitsC = {}
   
for ctau in results.keys():
    cv = ROOT.TCanvas("cv"+ctau,"",800,670)
    cv.SetLeftMargin(0.145)
    cv.SetRightMargin(0.195)
    cv.SetBottomMargin(0.14)
    cv.SetTopMargin(0.08)
    cv.SetLogz(1)
    xmin = 0.600
    ymin = 0
    xmax = 2.400
    ymax = 2.400
    zmax = 0.35
    zmin = 0.0004
    

    axis = ROOT.TH2F("axis"+ctau,";m#lower[0.2]{#scale[0.8]{#tilde{g}}} (TeV); m#lower[0.2]{#scale[0.8]{#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}}} (TeV)",
        int(round((xmax-xmin)/0.050)),numpy.linspace(xmin,xmax,int(round((xmax-xmin)/0.050))+1),
        int(round((ymax-ymin)/0.050)),numpy.linspace(ymin,ymax,int(round((ymax-ymin)/0.050))+1)
    )
    axis.Fill(-1,-1)
    '''
    for xbin in range(axis.GetNbinsX()):
        value = xmin+xbin*(xmax-xmin)/50
        if xbin%4==0:
            axis.GetXaxis().SetBinLabel(xbin+1,"%.0f"%axis.GetXaxis().GetBinCenter(xbin+1))
    '''
    axis.Draw("colz")    
    axis.GetZaxis().SetTitle("95% CL expected limit #sigma#lower[0.2]{#scale[0.8]{pp#rightarrow#tilde{g}#tilde{g}}} (pb)")
    axis.GetZaxis().SetRangeUser(zmin,zmax)
    
    axis.GetXaxis().SetNoExponent(True)
    #axis.GetXaxis().LabelsOption("v")
    axis.GetYaxis().SetNoExponent(True)
    axis.GetXaxis().SetNdivisions(510)
    axis.GetYaxis().SetNdivisions(510)
    

    limitHist = ROOT.TH2F("limitHist"+ctau,";m#lower[0.2]{#scale[0.8]{#tilde{g}}} (TeV); m#lower[0.2]{#scale[0.8]{#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}}} (TeV)",
        int(round((xmax-xmin)/0.050))+1,numpy.linspace(xmin-0.025,xmax+0.025,int(round((xmax-xmin)/0.010))+2),
        int(round((ymax-ymin)/0.050))+1,numpy.linspace(ymin-0.025,ymax+0.025,int(round((ymax-ymin)/0.010))+2)
    )
    boxes = []
    
    for llpMass in sorted(results[ctau].keys()):
        for lspMass in sorted(results[ctau][llpMass].keys()):
        
            if 0.001*int(llpMass)>xmax:
                continue
            if 0.001*int(lspMass)>ymax:
                continue
            limitHist.Fill(0.001*int(llpMass),0.001*int(lspMass),results[ctau][llpMass][lspMass]["median"])
            
            box= ROOT.TBox(
                max(xmin,min(xmax,0.001*int(llpMass)-0.018)),max(ymin,min(ymax,0.001*int(lspMass)-0.023)),
                max(xmin,min(xmax,0.001*int(llpMass)+0.018)),max(ymin,min(ymax,0.001*int(lspMass)+0.023))
            )
            box.SetFillColor(ROOT.kWhite)
            box.SetLineWidth(0)
            box.SetFillStyle(1001)
            boxes.append(box)
            
            '''
            marker= ROOT.TMarker(0.001*int(llpMass),0.001*int(lspMass),20)
            marker.SetMarkerColor(ROOT.kWhite)
            marker.SetMarkerSize(1.4)
            boxes.append(marker)
            '''
    
    limitFct = interpolatedLimitFct2(
        results[ctau],
        kind="median"
    )
    
    limitFctUp = interpolatedLimitFct2(
        results[ctau],
        kind="+1"
    )
    limitFctDown = interpolatedLimitFct2(
        results[ctau],
        kind="-1"
    )
    
    #print limitFct(600,0)
    
    '''
    limitHistSmooth = interpolatedHist(
        limitFct,
        numpy.linspace(xmin-0.025,xmax+0.025,(xmax-xmin)/0.010),
        numpy.linspace(ymin-0.025,ymax+0.025,(ymax-ymin)/0.010)
    )
    
    limitHistSmooth.GetZaxis().SetRangeUser(zmin,zmax)
    limitHistSmooth.Draw("colSame")
    '''
    limitHist.GetZaxis().SetRangeUser(zmin,zmax)
    #limitHist.Draw("colSame")
    
    for box in boxes:
        box.Draw("F")
        
    

    '''
    poly = ROOT.TPolyLine(3,
        numpy.array([0.600,2.400,0.600],dtype=numpy.float32), 
        numpy.array([0.600,2.400,2.400],dtype=numpy.float32),
    )
    poly.SetFillColor(ROOT.kGray)
    poly.SetFillStyle(3445)
    poly.Draw("F")
    '''
    
    
    
    xsecFct = getTheoryXsecFct("theory_xsec.dat")
    
    
    llpMassExpMedian = []
    lspMassExpMedian = []
    
    llpMassExpUp = []
    lspMassExpUp = []
    
    llpMassExpDown = []
    lspMassExpDown = []
    
    llpMassTheoUp = []
    lspMassTheoUp = []
    
    llpMassTheoDown = []
    lspMassTheoDown = []
    
    for angle in numpy.linspace(0.0,math.pi/4,50):
        foundMedian = False
        foundExpDown = False
        foundExpUp = False
        foundTheoDown = False
        foundTheoUp = False
        for r in numpy.linspace(2.600,0.600,1200):
            llpMass = r*math.cos(angle)
            lspMass = r*math.sin(angle)
            #print llpMass,lspMass
            if llpMass>(xmax) or lspMass>(ymax):
                continue
            if (llpMass-lspMass)<0.1:
                continue
            xsecTheo,xsecTheoUp,xsecTheoDown = xsecFct(llpMass*1000.)
            xsecLimit = limitFct(llpMass*1000.,lspMass*1000.)
            #print llpMass,lspMass,xsecLimit,xsecTheo
            xsecLimitUp = limitFctUp(llpMass*1000.,lspMass*1000.)
            xsecLimitDown = limitFctDown(llpMass*1000.,lspMass*1000.)
            
            if not foundMedian and xsecLimit<xsecTheo:
                llpMassExpMedian.append(llpMass)
                lspMassExpMedian.append(lspMass)
                foundMedian = True
                
            if not foundTheoDown and xsecLimit<xsecTheoDown:
                llpMassTheoDown.append(llpMass)
                lspMassTheoDown.append(lspMass)
                foundTheoDown = True
            if not foundTheoUp and xsecLimit<xsecTheoUp:
                llpMassTheoUp.append(llpMass)
                lspMassTheoUp.append(lspMass)
                foundTheoUp = True
                
            if not foundExpDown and xsecLimitDown<xsecTheo:
                llpMassExpDown.append(llpMass)
                lspMassExpDown.append(lspMass)
                foundExpDown = True
            if not foundExpUp and xsecLimitUp<xsecTheo:
                llpMassExpUp.append(llpMass)
                lspMassExpUp.append(lspMass)
                foundExpUp = True
                
            if foundExpDown and foundExpUp and foundTheoDown and foundTheoUp and foundMedian:
                break

                
    foundC=False
    foundU=False
    
    foundCExpUp=False
    foundUExpUp=False
    
    foundCExpDown=False
    foundUExpDown=False
    
    foundCTheoUp=False
    foundUTheoUp=False
    
    foundCTheoDown=False
    foundUTheoDown=False
    
    limitsC[ctau] = {}
    limitsU[ctau] = {}
    
    for k in ["mean","expUp","expDown","theoUp","theoDown"]:
        limitsC[ctau][k] = 0.
        limitsU[ctau][k] = 0.
    
    for r in numpy.linspace(3.000,0.600,1200):
        llpMass = r
        lspMassC = r-0.100
        lspMassU = 0.100
        
        xsecTheo,xsecTheoUp,xsecTheoDown = xsecFct(llpMass*1000.)
        
        xsecLimitC = limitFct(llpMass*1000.,lspMassC*1000.)
        xsecLimitCUp = limitFctUp(llpMass*1000.,lspMassC*1000.)
        xsecLimitCDown = limitFctDown(llpMass*1000.,lspMassC*1000.)
        
        if not foundC and xsecLimitC<xsecTheo:
            limitsC[ctau]["mean"]=llpMass
            foundC = True
            
        if not foundCExpUp and xsecLimitCUp<xsecTheo:
            limitsC[ctau]["expUp"]=llpMass
            foundCExpUp = True
        if not foundCExpDown and xsecLimitCDown<xsecTheo:
            limitsC[ctau]["expDown"]=llpMass
            foundCExpDown = True
            
        if not foundCTheoUp and xsecLimitC<xsecTheoUp:
            limitsC[ctau]["theoUp"]=llpMass
            foundCTheoUp = True
        if not foundCTheoDown and xsecLimitC<xsecTheoDown:
            limitsC[ctau]["theoDown"]=llpMass
            foundCTheoDown = True
        
        xsecLimitU = limitFct(llpMass*1000.,lspMassU*1000.)
        xsecLimitUUp = limitFctUp(llpMass*1000.,lspMassU*1000.)
        xsecLimitUDown = limitFctDown(llpMass*1000.,lspMassU*1000.)
        
        if not foundU and xsecLimitU<xsecTheo:
            limitsU[ctau]["mean"]=llpMass
            foundU = True
            
        if not foundUExpUp and xsecLimitUUp<xsecTheo:
            limitsU[ctau]["expUp"]=llpMass
            foundUExpUp = True
        if not foundUExpDown and xsecLimitUDown<xsecTheo:
            limitsU[ctau]["expDown"]=llpMass
            foundUExpDown = True
            
        if not foundUTheoUp and xsecLimitU<xsecTheoUp:
            limitsU[ctau]["theoUp"]=llpMass
            foundUTheoUp = True
        if not foundUTheoDown and xsecLimitU<xsecTheoDown:
            limitsU[ctau]["theoDown"]=llpMass
            foundUTheoDown = True
        
    print ctau,"compress: %.3f %+.3f %+.3f (exp) %+.3f %+.3f (theo)"%(
        limitsC[ctau]["mean"],
        limitsC[ctau]["expUp"]-limitsC[ctau]["mean"],
        limitsC[ctau]["expDown"]-limitsC[ctau]["mean"],
        limitsC[ctau]["theoUp"]-limitsC[ctau]["mean"],
        limitsC[ctau]["theoDown"]-limitsC[ctau]["mean"],
    )
    print ctau,"uncompress: %.3f %+.3f %+.3f (exp) %+.3f %+.3f (theo)"%(
        limitsU[ctau]["mean"],
        limitsU[ctau]["expUp"]-limitsU[ctau]["mean"],
        limitsU[ctau]["expDown"]-limitsU[ctau]["mean"],
        limitsU[ctau]["theoUp"]-limitsU[ctau]["mean"],
        limitsU[ctau]["theoDown"]-limitsU[ctau]["mean"],
    )
    
        
    llpMassTheo = llpMassTheoUp+list(reversed(llpMassTheoDown))
    lspMassTheo = lspMassTheoUp+list(reversed(lspMassTheoDown))
        
        
    llpMassExpMedian = numpy.array(llpMassExpMedian)
    lspMassExpMedian = numpy.array(lspMassExpMedian)
    
    llpMassExpUp = numpy.array(llpMassExpUp)
    lspMassExpUp = numpy.array(lspMassExpUp)
    
    llpMassExpDown = numpy.array(llpMassExpDown)
    lspMassExpDown = numpy.array(lspMassExpDown)
    
    llpMassTheoUp = numpy.array(llpMassTheoUp)
    lspMassTheoUp = numpy.array(lspMassTheoUp)
    
    llpMassTheoDown = numpy.array(llpMassTheoDown)
    lspMassTheoDown = numpy.array(lspMassTheoDown)
    
    llpMassTheo = numpy.array(llpMassTheo)
    lspMassTheo = numpy.array(lspMassTheo)
    
    
    polyTheoUp = ROOT.TPolyLine(
        len(llpMassTheo),
        llpMassTheo,
        lspMassTheo
    )
    polyTheoUp.SetFillColor(ROOT.kGray)
    polyTheoUp.SetFillStyle(3354)
    polyTheoUp.Draw("F")
    
    polyExpMedian = ROOT.TPolyLine(
        len(llpMassExpMedian),
        llpMassExpMedian,
        lspMassExpMedian
    )
    polyExpMedian.SetLineColor(ROOT.kBlack)
    polyExpMedian.SetLineWidth(3)
    polyExpMedian.Draw("L")
    
    polyExpDown = ROOT.TPolyLine(
        len(llpMassExpDown),
        llpMassExpDown,
        lspMassExpDown
    )
    polyExpDown.SetLineColor(ROOT.kBlack)
    polyExpDown.SetLineWidth(2)
    polyExpDown.SetLineStyle(2)
    polyExpDown.Draw("L")
    
    polyExpUp = ROOT.TPolyLine(
        len(llpMassExpUp),
        llpMassExpUp,
        lspMassExpUp
    )
    polyExpUp.SetLineColor(ROOT.kBlack)
    polyExpUp.SetLineWidth(2)
    polyExpUp.SetLineStyle(2)
    polyExpUp.Draw("L")
    
    '''
    polyTheoDown = ROOT.TPolyLine(
        len(llpMassTheoDown),
        llpMassTheoDown,
        lspMassTheoDown
    )
    polyTheoDown.SetLineColor(ROOT.kBlack)
    polyTheoDown.SetLineWidth(2)
    polyTheoDown.SetLineStyle(12)
    polyTheoDown.Draw("L")
    
    polyTheoUp = ROOT.TPolyLine(
        len(llpMassTheoUp),
        llpMassTheoUp,
        lspMassTheoUp
    )
    polyTheoUp.SetLineColor(ROOT.kBlack)
    polyTheoUp.SetLineWidth(2)
    polyTheoUp.SetLineStyle(12)
    polyTheoUp.Draw("L")
    '''
    
    '''
    polyTheoUp2 = ROOT.TPolyLine(
        len(llpMassTheo),
        llpMassTheo,
        lspMassTheo
    )
    polyTheoUp2.SetLineColor(ROOT.kGray+2)
    polyTheoUp2.SetLineWidth(2)
    polyTheoUp2.Draw("L")
    '''
    '''
    pad = ROOT.TBox(xmin+0.15,ymax-0.15,xmin+0.7,ymax-0.7)
    pad.SetFillColor(ROOT.kWhite)
    pad.Draw("SameF")
    '''
    line1 = ROOT.TLine(xmin+0.2,ymax-0.25,xmin+0.4,ymax-0.25)
    line1.SetLineWidth(3)
    line1.SetLineColor(ROOT.kBlack)
    line1.Draw("Same")
    line2 = ROOT.TLine(xmin+0.2,ymax-0.2,xmin+0.4,ymax-0.2)
    line2.SetLineWidth(2)
    line2.SetLineStyle(2)
    line2.SetLineColor(ROOT.kBlack)
    line2.Draw("Same")
    line3 = ROOT.TLine(xmin+0.2,ymax-0.3,xmin+0.4,ymax-0.3)
    line3.SetLineWidth(2)
    line3.SetLineStyle(2)
    line3.SetLineColor(ROOT.kBlack)
    line3.Draw("Same")
    pText1 = ROOT.TPaveText(xmin+0.5,ymax-0.25,xmin+0.5,ymax-0.25)
    pText1.SetFillStyle(0)
    pText1.SetBorderSize(0)
    pText1.SetTextFont(43)
    pText1.SetTextSize(29)
    pText1.SetTextAlign(12)
    pText1.AddText("Syst. unc.")
    pText1.Draw("Same")
    
    box1 = ROOT.TBox(xmin+0.2,ymax-0.45,xmin+0.4,ymax-0.55)
    box1.SetFillColor(ROOT.kGray)
    box1.SetFillStyle(3354)
    box1.Draw("SameF")
    line4 = ROOT.TLine(xmin+0.2,ymax-0.5,xmin+0.4,ymax-0.5)
    line4.SetLineWidth(3)
    line4.SetLineColor(ROOT.kBlack)
    line4.Draw("Same")
    pText2= ROOT.TPaveText(xmin+0.5,ymax-0.5,xmin+0.5,ymax-0.5)
    pText2.SetFillStyle(0)
    pText2.SetBorderSize(0)
    pText2.SetTextFont(43)
    pText2.SetTextSize(29)
    pText2.SetTextAlign(12)
    pText2.AddText("Theo. unc.")
    pText2.Draw("Same")
    
    ROOT.gPad.RedrawAxis()
    
    pTextCMS = ROOT.TPaveText(cv.GetLeftMargin(),1-cv.GetTopMargin()*0.4,cv.GetLeftMargin(),1-cv.GetTopMargin()*0.4,"NDC")
    pTextCMS.AddText("CMS")
    pTextCMS.SetTextFont(63)
    pTextCMS.SetTextSize(32)
    pTextCMS.SetTextAlign(13)
    pTextCMS.Draw("Same")
    
    pTextPreliminary = ROOT.TPaveText(cv.GetLeftMargin()+0.088,1-cv.GetTopMargin()*0.4,cv.GetLeftMargin()+0.088,1-cv.GetTopMargin()*0.4,"NDC")
    pTextPreliminary.AddText("Simulation")
    pTextPreliminary.SetTextFont(53)
    pTextPreliminary.SetTextSize(32)
    pTextPreliminary.SetTextAlign(13)
    pTextPreliminary.Draw("Same")

    pTextCTau = ROOT.TPaveText(1-cv.GetRightMargin(),1-cv.GetTopMargin()*0.4,1-cv.GetRightMargin(),1-cv.GetTopMargin()*0.4,"NDC")
    pTextCTau.AddText("c#tau#kern[-0.5]{ }=#kern[-0.8]{ }%s"%ctauLabels[ctau])
    pTextCTau.SetTextFont(43)
    pTextCTau.SetTextSize(32)
    pTextCTau.SetTextAlign(33)
    pTextCTau.Draw("Same")
    
    #cv.Print(os.path.join(basePath,"limits_ctau%s.pdf"%ctau))
    #cv.Print(os.path.join(basePath,"limits_ctau%s.png"%ctau))
    
    
resultFile = open(os.path.join(basePath,"summary.json"),"w")
json.dump({"compressed":limitsC,"uncompressed":limitsU}, resultFile)
resultFile.close()




