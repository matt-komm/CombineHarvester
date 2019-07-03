import os
import sys
import numpy
import math
import ROOT
import random
import json
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

colorList = [
    [0.,newColorHLS(0.6, 0.47,0.6)],
    [0.,newColorHLS(0.56, 0.65, 0.7)],
    [0.,newColorHLS(0.52, 1., 1.)],
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
    

SUS_16_038 = {
    'ctau_values':range(0,10),
    'exp':{'mchi_0':{'mgl':[1765,1758,1788,1925,1841,1664,1407,1087,1040],
                     'mlsp':[1,0,0,1,0,1,1,0,0]},
           'mchi_100':{'mgl':[1777,1774,1795,1931,1844,1673,1405,1096,1035],
                       'mlsp':[102,101,100,101,100,101,101,101,101]},
           'dm_100':{'mgl':[1110,1093,1123,1231,1203,1094,1020,1006,1002],
                     'mlsp':[1010,993,1023,1132,1104,994,921,906,901]},
           'dm_10':{'mgl':[1038,1027,1051,1129,1097,1485,1029,967,981,1004],
                    'mlsp':[1029,1016,1040,1120,1087,1,1019,959,971,994]}},
    'obs':{'mchi_0':{'mgl':[1629,1620,1589,1740,1630,1485,1301,966,886],
                     'mlsp':[1,1,0,1,0,1,0,0,0]},
           'mchi_100':{'mgl':[1624,1625,1605,1750,1631,1485,1293,984,901],
                       'mlsp':[100,102,100,101,100,100,101,100,101]},
           'dm_100':{'mgl':[1034,1061,1102,1141,1036,985,898,865,934],
                     'mlsp':[934,960,1003,1041,936,884,796,766,825]},
           'dm_10':{'mgl':[964,997,1013,1041,961,954,836,842,909],
                    'mlsp':[953,988,1003,1030,951,943,827,831,900,]}},
    'prompt':{'mchi_0':{'mgl':{'exp':1800,'obs':1628},
                        'mlsp':{'exp':0,'obs':0}},
              'mchi_100':{'mgl':{'exp':1792,'obs':1638},
                          'mlsp':{'exp':102,'obs':102}},
              'dm_100':{'mgl':{'exp':1017,'obs':942},
                        'mlsp':{'exp':917,'obs':843}}},
    'stable':{'mchi_0':{'mgl':{'exp':1003,'obs':906},
                        'mlsp':{'exp':0,'obs':0}},
              'mchi_100':{'mgl':{'exp':1003,'obs':906},
                          'mlsp':{'exp':100,'obs':100}},
              'dm_100':{'mgl':{'exp':1003,'obs':906},
                        'mlsp':{'exp':903,'obs':806}},
              'dm_10':{'mgl':{'exp':1003,'obs':906},
                       'mlsp':{'exp':903,'obs':806}}},
}

with open('eventyields.json',) as f:
    genweights = json.load(f)

ctauValues = ["0p001","0p01","0p1","1","10","100","1000","10000"]
#ctauValues = ["0p1","1","10","100","1000","10000"]
#ctauValues = ["10"]
ctauLabels = {
    "0p001":"1#kern[-0.5]{ }#mum",
    "0p01":"10#kern[-0.5]{ }#mum",
    "0p1":"100#kern[-0.5]{ }#mum",
    "1":"1#kern[-0.5]{ }mm",
    "10":"10#kern[-0.5]{ }mm",
    "100":"100#kern[-0.5]{ }mm",
    "1000":"1#kern[-0.5]{ }m",
    "10000":"10#kern[-0.5]{ }m",
}
ctauValueMap = {
    "0p001":0,
    "0p01":1,
    "0p1":2,
    "1":3,
    "10":4,
    "100":5,
    "1000":6,
    "10000":7,
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

basePath = "limits"

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
    zmin = 0.0005

    axis = ROOT.TH2F("axis"+ctau,";m#lower[0.2]{#scale[0.8]{#tilde{g}}} (TeV); m#lower[0.2]{#scale[0.8]{#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}}} (TeV)",
        int(round((xmax-xmin)/0.050))+1,numpy.linspace(xmin-0.025,xmax+0.025,int(round((xmax-xmin)/0.050))+2),
        int(round((ymax-ymin)/0.050))+1,numpy.linspace(ymin-0.025,ymax+0.025,int(round((ymax-ymin)/0.050))+2)
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
        int(round((xmax-xmin)/0.050))+1,numpy.linspace(xmin-0.025,xmax+0.025,int(round((xmax-xmin)/0.050))+2),
        int(round((ymax-ymin)/0.050))+1,numpy.linspace(ymin-0.025,ymax+0.025,int(round((ymax-ymin)/0.050))+2)
    )
    boxes = []
    for llpMass in sorted(results[ctau].keys()):
        for lspMass in sorted(results[ctau][llpMass].keys()):
        
            if 0.001*int(llpMass)>xmax:
                continue
            if 0.001*int(lspMass)>ymax:
                continue
            limitHist.Fill(0.001*int(llpMass),0.001*int(lspMass),results[ctau][llpMass][lspMass]["median"])
            '''
            box= ROOT.TBox(0.001*int(llpMass)-0.025,0.001*int(lspMass)-0.025,0.001*int(llpMass)+0.025,0.001*int(lspMass)+0.025)
            box.SetFillColor(ROOT.kGray)
            box.SetLineWidth(0)
            box.SetFillStyle(1001)
            boxes.append(box)
            '''
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
    limitHist.Draw("colSame")
    
    for box in boxes:
        box.Draw("L")
    
    
    poly = ROOT.TPolyLine(3,
        numpy.array([0.600-0.025,2.400+0.025,0.600-0.025],dtype=numpy.float32), 
        numpy.array([0.600-0.025,2.400+0.025,2.400+0.025],dtype=numpy.float32),
    )
    poly.SetFillColor(ROOT.kGray)
    poly.SetFillStyle(3445)
    poly.Draw("F")
    
    
    
    
    xsecFct = getTheoryXsecFct("theory_xsec.dat")
    
    
    llpMassExpMedian = []
    lspMassExpMedian = []
    
    llpMassExpUp = []
    lspMassExpUp = []
    
    llpMassExpDown = []
    lspMassExpDown = []
    
    for angle in numpy.linspace(0.0,math.pi/4,5):
        foundDown = False
        foundMedian = False
        foundUp = False
        for r in numpy.linspace(2.600,0.600,10):
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
            if not foundDown and xsecLimitDown<xsecTheo:
                llpMassExpDown.append(llpMass)
                lspMassExpDown.append(lspMass)
                foundDown = True
            if not foundMedian and xsecLimit<xsecTheo:
                llpMassExpMedian.append(llpMass)
                lspMassExpMedian.append(lspMass)
                foundMedian = True
            if not foundUp and xsecLimitUp<xsecTheo:
                llpMassExpUp.append(llpMass)
                lspMassExpUp.append(lspMass)
                foundUp = True
            if foundDown and foundMedian and foundUp:
                break
    #print llpMassExpMedian
    #print lspMassExpMedian
                
    foundC=False
    foundU=False
    for r in numpy.linspace(3.000,0.600,1200):
        llpMassC = r
        lspMassC = r-0.100
        llpMassU = r
        lspMassU = 0.100
        
        xsecTheoC,_,_ = xsecFct(llpMassC*1000.)
        xsecLimitC = limitFct(llpMassC*1000.,lspMassC*1000.)
        if not foundC and xsecLimitC<xsecTheoC:
            limitsC[ctau]=llpMassC
            foundC = True
        
        xsecTheoU,_,_ = xsecFct(llpMassU*1000.)
        xsecLimitU = limitFct(llpMassU*1000.,lspMassU*1000.)
        if not foundU and xsecLimitU<xsecTheoU:
            limitsU[ctau]=llpMassU
            foundU = True
            
        if foundC and foundU:
            break
        
    if not foundC:
        limitsC[ctau]=0
    if not foundU:
        limitsU[ctau]=0
        
    llpMassExpMedian = numpy.array(llpMassExpMedian)
    lspMassExpMedian = numpy.array(lspMassExpMedian)
    
    llpMassExpUp = numpy.array(llpMassExpUp)
    lspMassExpUp = numpy.array(lspMassExpUp)
    
    llpMassExpDown = numpy.array(llpMassExpDown)
    lspMassExpDown = numpy.array(lspMassExpDown)
    
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
    
    ROOT.gPad.RedrawAxis()
    
    pTextCMS = ROOT.TPaveText(cv.GetLeftMargin(),1-cv.GetTopMargin()*0.4,cv.GetLeftMargin(),1-cv.GetTopMargin()*0.4,"NDC")
    pTextCMS.AddText("CMS")
    pTextCMS.SetTextFont(63)
    pTextCMS.SetTextSize(32)
    pTextCMS.SetTextAlign(13)
    pTextCMS.Draw("Same")
    
    pTextPreliminary = ROOT.TPaveText(cv.GetLeftMargin()+0.08,1-cv.GetTopMargin()*0.4,cv.GetLeftMargin()+0.08,1-cv.GetTopMargin()*0.4,"NDC")
    pTextPreliminary.AddText("Preliminary")
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
    
    cv.Print("limits_ctau%s.pdf"%ctau)
    cv.Print("limits_ctau%s.png"%ctau)
    
xvalues = numpy.logspace(-6,1,num=8)
#xvalues = numpy.power(10,xvalues)
yvaluesC = numpy.zeros(8)
yvaluesU = numpy.zeros(8)

yvaluesC_SUS = numpy.zeros(8)
yvaluesU_SUS = numpy.zeros(8)

for ctau in limitsU.keys():
    yvaluesC[ctauValueMap[ctau]]=limitsC[ctau]
    yvaluesU[ctauValueMap[ctau]]=limitsU[ctau]
    
    yvaluesC_SUS[ctauValueMap[ctau]] = SUS_16_038['exp']['dm_100']['mgl'][ctauValueMap[ctau]]/1000.
    
    yvaluesU_SUS[ctauValueMap[ctau]] = SUS_16_038['exp']['mchi_100']['mgl'][ctauValueMap[ctau]]/1000.
    
    print ctau,limitsC[ctau],limitsU[ctau]
    
cv = ROOT.TCanvas("summary","",800,670)
#cv.SetGridx(True)
#cv.SetGridy(True)
#cv.SetLogx(1)
#cv.SetMargin(0.155,0.04,0.15,0.065)

cvxmin = 0.135
cvxmax = 0.965
cvymin = 0.125
cvymax = 0.94

cv.Divide(1,2,0,0)
cv.GetPad(1).SetPad(0.0, 0.0, 1.0, 1.0)
cv.GetPad(1).SetFillStyle(4000)
cv.GetPad(2).SetPad(0.0, 0.00, 1.0,1.0)
cv.GetPad(2).SetFillStyle(4000)
        
for i in [1,2]:
    #for the canvas:
    cv.GetPad(i).SetBorderMode(0)
    cv.GetPad(i).SetGridx(False)
    cv.GetPad(i).SetGridy(False)


    #For the frame:
    cv.GetPad(i).SetFrameBorderMode(0)
    cv.GetPad(i).SetFrameBorderSize(1)
    cv.GetPad(i).SetFrameFillColor(0)
    cv.GetPad(i).SetFrameFillStyle(0)
    cv.GetPad(i).SetFrameLineColor(1)
    cv.GetPad(i).SetFrameLineStyle(1)
    cv.GetPad(i).SetFrameLineWidth(1)

    # Margins:
    cv.GetPad(i).SetLeftMargin(cvxmin)
    cv.GetPad(i).SetRightMargin(1-cvxmax)
    
    # For the Global title:
    cv.GetPad(i).SetTitle("")
    
    # For the axis:
    cv.GetPad(i).SetTickx(1)  # To get tick marks on the opposite side of the frame
    cv.GetPad(i).SetTicky(1)

    # Change for log plots:
    cv.GetPad(i).SetLogx(1)
    cv.GetPad(i).SetLogy(0)
    cv.GetPad(i).SetLogz(0)

cv.GetPad(2).SetTopMargin(1-cvymax)
cv.GetPad(2).SetBottomMargin(cvymin+.5*(cvymax-cvymin)+0.007)
cv.GetPad(1).SetTopMargin(1-(cvymin+.5*(cvymax-cvymin))+0.007)
cv.GetPad(1).SetBottomMargin(cvymin)

cv.cd(1)
axis1 = ROOT.TH2F("axis",";c#tau (m);",
    50,10**-6.2,10**1.2,
    50,0.0,0.0+2.1
)
axis1.GetXaxis().SetTickLength(0.017/(1-cv.GetPad(1).GetLeftMargin()-cv.GetPad(1).GetRightMargin()))
axis1.GetYaxis().SetTickLength(0.015/(1-cv.GetPad(1).GetTopMargin()-cv.GetPad(1).GetBottomMargin()))
axis1.Draw("AXIS")

cv.cd(2)
axis2 = ROOT.TH2F("axis",";;95% CL lower limit on m#lower[0.2]{#scale[0.8]{#tilde{g}}} (TeV)",
    50,10**-6.2,10**1.2,
    50,0.6,0.6+2.1
)
axis2.GetXaxis().SetTickLength(0.017/(1-cv.GetPad(2).GetLeftMargin()-cv.GetPad(2).GetRightMargin()))
axis2.GetYaxis().SetTickLength(0.015/(1-cv.GetPad(2).GetTopMargin()-cv.GetPad(2).GetBottomMargin()))
axis2.GetXaxis().SetTitleSize(0)
axis2.GetXaxis().SetLabelSize(0)
axis2.Draw("AXIS")


colorU = newColorHLS(0.76,0.7,0.95)
colorU_SUS = newColorHLS(0.68,0.4,0.8)

colorC = newColorHLS(0.07,0.6,0.95)
colorC_SUS = newColorHLS(0.0,0.4,0.8)


cv.cd(1)

graphC_SUS = ROOT.TGraph(8,xvalues,yvaluesC_SUS)
graphC_SUS.SetLineColor(colorC_SUS.GetNumber())
graphC_SUS.SetLineWidth(3)
graphC_SUS.SetLineStyle(2)
graphC_SUS.SetMarkerStyle(24)
graphC_SUS.SetMarkerSize(2)
graphC_SUS.SetMarkerColor(colorC_SUS.GetNumber())
graphC_SUS.Draw("PL")

graphC = ROOT.TGraph(8,xvalues,yvaluesC)
graphC.SetLineColor(colorC.GetNumber())
graphC.SetLineWidth(2)
graphC.SetLineStyle(1)
graphC.SetMarkerStyle(20)
graphC.SetMarkerSize(1.7)
graphC.SetMarkerColor(colorC.GetNumber())
graphC.Draw("PL")

cv.cd(2)

graphU_SUS = ROOT.TGraph(8,xvalues,yvaluesU_SUS)
graphU_SUS.SetLineColor(colorU_SUS.GetNumber())
graphU_SUS.SetLineWidth(3)
graphU_SUS.SetLineStyle(2)
graphU_SUS.SetMarkerStyle(24)
graphU_SUS.SetMarkerSize(2)
graphU_SUS.SetMarkerColor(colorU_SUS.GetNumber())
graphU_SUS.Draw("PL")

graphU = ROOT.TGraph(8,xvalues,yvaluesU)
graphU.SetLineColor(colorU.GetNumber())
graphU.SetLineWidth(2)
graphU.SetLineStyle(1)
graphU.SetMarkerStyle(20)
graphU.SetMarkerSize(1.7)
graphU.SetMarkerColor(colorU.GetNumber())
graphU.Draw("PL")

cv.cd(2)

pTextCMS = ROOT.TPaveText(cvxmin,cvymax+0.05,cvxmin,cvymax+0.05,"NDC")
pTextCMS.AddText("CMS")
pTextCMS.SetTextFont(63)
pTextCMS.SetTextSize(31)
pTextCMS.SetTextAlign(13)
pTextCMS.Draw("Same")

pTextPreliminary = ROOT.TPaveText(cvxmin+0.09,cvymax+0.05,cvxmin+0.09,cvymax+0.05,"NDC")
pTextPreliminary.AddText("Simulation")
pTextPreliminary.SetTextFont(53)
pTextPreliminary.SetTextSize(31)
pTextPreliminary.SetTextAlign(13)
pTextPreliminary.Draw("Same")

pLumi = ROOT.TPaveText(cvxmax,cvymax+0.05,cvxmax,cvymax+0.05,"NDC")
pLumi.AddText("35.9 fb#lower[-0.8]{#scale[0.7]{-1}} (13 TeV)")
pLumi.SetTextFont(43)
pLumi.SetTextSize(31)
pLumi.SetTextAlign(33)
pLumi.Draw("Same")

pInfo1 = ROOT.TPaveText(cvxmin+0.03,1-cv.GetPad(1).GetTopMargin()-0.02,cvxmin+0.03,1-cv.GetPad(1).GetTopMargin()-0.02,"NDC")
pInfo1.AddText("pp#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }"+gSymbol+"#kern[-0.6]{ }"+gSymbol+", "+gSymbol+"#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }q#kern[-0.7]{ }q#lower[-0.8]{#kern[-0.89]{#minus}}#kern[-0.6]{ }"+chiSymbol+"#kern[-0.8]{ }, "+mgSymbol+"#kern[-0.2]{ }#minus#kern[-0.2]{ }"+mchiSymbol+" =#kern[-0.2]{ }100#kern[-0.4]{ }GeV")
pInfo1.SetTextFont(43)
pInfo1.SetTextSize(27)
pInfo1.SetTextAlign(13)
pInfo1.Draw("Same")

legend1 = ROOT.TLegend(cvxmin+0.03,cv.GetPad(1).GetBottomMargin()+0.02+0.085,cvxmin+0.03+0.45,cv.GetPad(1).GetBottomMargin()+0.02)
legend1.SetFillStyle(0)
legend1.SetBorderSize(0)
legend1.SetTextFont(43)
legend1.SetTextSize(27)
legend1.AddEntry(graphC,"Displaced jet tagger","PL")
legend1.AddEntry(graphC_SUS,"#scale[0.9]{#font[82]{arXiv:1802.02110}}","PL")
legend1.Draw("Same")

pInfo2 = ROOT.TPaveText(cvxmin+0.03,1-cv.GetPad(2).GetTopMargin()-0.02,cvxmin+0.03,1-cv.GetPad(2).GetTopMargin()-0.02,"NDC")
pInfo2.AddText("pp#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }"+gSymbol+"#kern[-0.6]{ }"+gSymbol+", "+gSymbol+"#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }q#kern[-0.7]{ }q#lower[-0.8]{#kern[-0.89]{#minus}}#kern[-0.6]{ }"+chiSymbol+"#kern[-0.8]{ }, "+mchiSymbol+" =#kern[-0.2]{ }100#kern[-0.4]{ }GeV")
pInfo2.SetTextFont(43)
pInfo2.SetTextSize(27)
pInfo2.SetTextAlign(13)
pInfo2.Draw("Same")

legend2 = ROOT.TLegend(cvxmin+0.03,cv.GetPad(2).GetBottomMargin()+0.02+0.085,cvxmin+0.03+0.45,cv.GetPad(2).GetBottomMargin()+0.02)
legend2.SetFillStyle(0)
legend2.SetBorderSize(0)
legend2.SetTextFont(43)
legend2.SetTextSize(27)
legend2.AddEntry(graphU,"Displaced jet tagger","PL")
legend2.AddEntry(graphU_SUS,"#scale[0.9]{#font[82]{arXiv:1802.02110}}","PL")

#legend2.AddEntry(graphU,"#kern[-0.5]{ }m#lower[0.2]{#scale[0.8]{#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}}}#kern[-0.4]{ }=#kern[-0.5]{ }100#kern[-0.6]{ }GeV","PL")
#legend2.AddEntry(graphC,"m#lower[0.2]{#scale[0.8]{#tilde{g}}}#kern[-0.5]{ }-#kern[-0.5]{ }m#lower[0.2]{#scale[0.8]{#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}}}#kern[-0.4]{ }=#kern[-0.5]{ }100#kern[-0.6]{ }GeV","PL")
legend2.Draw("Same")

cv.Print("summary.pdf")
cv.Print("summary.C")
cv.Print("summary.png")



