#!/usr/bin/env python
import ROOT
import math
import numpy
import os
import ctypes
import scipy
import scipy.interpolate

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetOptFit()
ROOT.gStyle.SetOptStat(0)

# For the canvas:
ROOT.gStyle.SetCanvasBorderMode(0)
ROOT.gStyle.SetCanvasColor(ROOT.kWhite)

# For the Pad:
ROOT.gStyle.SetPadBorderMode(0)
ROOT.gStyle.SetPadColor(ROOT.kWhite)
ROOT.gStyle.SetGridColor(ROOT.kBlack)
ROOT.gStyle.SetGridStyle(2)
ROOT.gStyle.SetGridWidth(1)

# For the frame:

ROOT.gStyle.SetFrameBorderMode(0)
ROOT.gStyle.SetFrameBorderSize(0)
ROOT.gStyle.SetFrameFillColor(0)
ROOT.gStyle.SetFrameFillStyle(0)
ROOT.gStyle.SetFrameLineColor(1)
ROOT.gStyle.SetFrameLineStyle(1)
ROOT.gStyle.SetFrameLineWidth(0)

# For the histo:
# ROOT.gStyle.SetHistFillColor(1)
# ROOT.gStyle.SetHistFillStyle(0)
# ROOT.gStyle.SetLegoInnerR(Float_t rad = 0.5)
# ROOT.gStyle.SetNumberContours(Int_t number = 20)

ROOT.gStyle.SetEndErrorSize(2)
#ROOT.gStyle.SetErrorMarker(20)
ROOT.gStyle.SetErrorX(0.)

ROOT.gStyle.SetMarkerStyle(20)
#ROOT.gStyle.SetMarkerStyle(20)

#For the fit/function:
ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetFitFormat("5.4g")
ROOT.gStyle.SetFuncColor(2)
ROOT.gStyle.SetFuncStyle(1)
ROOT.gStyle.SetFuncWidth(1)

#For the date:
ROOT.gStyle.SetOptDate(0)
# ROOT.gStyle.SetDateX(Float_t x = 0.01)
# ROOT.gStyle.SetDateY(Float_t y = 0.01)

# For the statistics box:
ROOT.gStyle.SetOptFile(0)
ROOT.gStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
ROOT.gStyle.SetStatColor(ROOT.kWhite)
ROOT.gStyle.SetStatFont(42)
ROOT.gStyle.SetStatFontSize(0.025)
ROOT.gStyle.SetStatTextColor(1)
ROOT.gStyle.SetStatFormat("6.4g")
ROOT.gStyle.SetStatBorderSize(1)
ROOT.gStyle.SetStatH(0.1)
ROOT.gStyle.SetStatW(0.15)

ROOT.gStyle.SetHatchesSpacing(0.8)
ROOT.gStyle.SetHatchesLineWidth(2)


ROOT.gStyle.SetOptTitle(0)

# For the axis titles:
ROOT.gStyle.SetTitleColor(1, "XYZ")
ROOT.gStyle.SetTitleFont(43, "XYZ")
ROOT.gStyle.SetTitleSize(33, "XYZ")
# ROOT.gStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
# ROOT.gStyle.SetTitleYSize(Float_t size = 0.02)
ROOT.gStyle.SetTitleXOffset(1.135)
#ROOT.gStyle.SetTitleYOffset(1.2)
ROOT.gStyle.SetTitleOffset(1.32, "YZ") # Another way to set the Offset

# For the axis labels:

ROOT.gStyle.SetLabelColor(1, "XYZ")
ROOT.gStyle.SetLabelFont(43, "XYZ")
ROOT.gStyle.SetLabelSize(29, "XYZ")
#ROOT.gStyle.SetLabelSize(0.04, "XYZ")

# For the axis:

ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetStripDecimals(True)
ROOT.gStyle.SetNdivisions(1005, "X")
ROOT.gStyle.SetNdivisions(506, "Y")

ROOT.gStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
ROOT.gStyle.SetPadTickY(1)

# Change for log plots:
ROOT.gStyle.SetOptLogx(0)
ROOT.gStyle.SetOptLogy(0)
ROOT.gStyle.SetOptLogz(0)

#ROOT.gStyle.SetPalette(1) #(1,0)

# another top group addition

# Postscript options:
#ROOT.gStyle.SetPaperSize(20., 20.)
#ROOT.gStyle.SetPaperSize(ROOT.TStyle.kA4)
#ROOT.gStyle.SetPaperSize(27., 29.7)
#ROOT.gStyle.SetPaperSize(27., 29.7)
ROOT.gStyle.SetPaperSize(8.0*1.35,6.7*1.35)
ROOT.TGaxis.SetMaxDigits(3)
ROOT.gStyle.SetLineScalePS(2)

# ROOT.gStyle.SetLineStyleString(Int_t i, const char* text)
# ROOT.gStyle.SetHeaderPS(const char* header)
# ROOT.gStyle.SetTitlePS(const char* pstitle)
#ROOT.gStyle.SetColorModelPS(1)

# ROOT.gStyle.SetBarOffset(Float_t baroff = 0.5)
# ROOT.gStyle.SetBarWidth(Float_t barwidth = 0.5)
# ROOT.gStyle.SetPaintTextFormat(const char* format = "g")
# ROOT.gStyle.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
# ROOT.gStyle.SetTimeOffset(Double_t toffset)
# ROOT.gStyle.SetHistMinimumZero(kTRUE)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetPaintTextFormat(".1f")

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
    #color[0] = ((lumiMax-color[1].GetLight())/(lumiMax-lumiMin))
    color[0] = ((color[1].GetLight()-lumiMin)/(lumiMax-lumiMin))


stops = numpy.array(map(lambda x:x[0],colorList))
red   = numpy.array(map(lambda x:x[1].GetRed(),colorList))
green = numpy.array(map(lambda x:x[1].GetGreen(),colorList))
blue  = numpy.array(map(lambda x:x[1].GetBlue(),colorList))

start=ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, 200)
ROOT.gStyle.SetNumberContours(200)



def getSigResult(f):
    inputFile = ROOT.TFile(f)
    limitTree = inputFile.Get("limit")
    if limitTree.GetEntries()==0:
        return -1
    limitTree.GetEntry(0)
    return limitTree.limit

def getScanResult(f):
    inputFile = ROOT.TFile(f)
    limitTree = inputFile.Get("limit")
    nEntries = limitTree.GetEntries()-1

    deltaNLL = numpy.zeros(nEntries)
    llpEff = numpy.zeros(nEntries)

    #entry 0 is best fit
    limitTree.GetEntry(0)
    deltaNLL_best = 2*limitTree.deltaNLL
    llpEff_best = limitTree.llpEff


    for entry in range(1,nEntries):
        limitTree.GetEntry(entry)
        deltaNLL[entry] = 2.*limitTree.deltaNLL
        llpEff[entry] = limitTree.llpEff
        
    index_best = numpy.argmin(numpy.fabs(llpEff-llpEff_best))
    #print index_best,llpEff[index_best],deltaNLL[index_best]

    sigma1_hi = -1.
    sigma1_lo = -1.

    sigma2_hi = -1.
    sigma2_lo = -1.

    for i in range(index_best,nEntries-1):
        if (deltaNLL[i]<=1.) and (deltaNLL[i+1]>1.):
            sigma1_hi = llpEff[i]
        if (deltaNLL[i]<=4.) and (deltaNLL[i+1]>4.):
            sigma2_hi = llpEff[i]
            
    for i in reversed(range(2,index_best)):
        if (deltaNLL[i]<=1.) and (deltaNLL[i-1]>1.):
            sigma1_lo = llpEff[i]
        if (deltaNLL[i]<=4.) and (deltaNLL[i-1]>4.):
            sigma2_lo = llpEff[i]
            
    #print sigma1_lo,sigma1_hi
    #print sigma2_lo,sigma2_hi
    
    '''
    cv = ROOT.TCanvas("cv","",800,600)
    graph = ROOT.TGraph(nEntries,llpEff,2.*deltaNLL)
    graph.Draw("APL")
    cv.WaitPrimitive()
    '''
    return {"1s": [sigma1_lo,sigma1_hi],"2s":[sigma2_lo,sigma2_hi],'llpEff':llpEff,'deltaNLL':deltaNLL}
    
    
def interpolate(grid):
    xvalues = numpy.array(grid['logmu'])
    yvalues = numpy.array(grid['llpEff'])
    zvalues = numpy.array(grid['deltaNLL'])
    
    def getValue(logmu,llpEff):
        distances = numpy.sqrt(numpy.square(xvalues-logmu)+numpy.square(yvalues-llpEff))
        
        minIndex = numpy.argmin(distances)
        return zvalues[minIndex]
        
        '''
        sortedIndices = numpy.argsort(distances)
        distances = distances[sortedIndices[0:10]]
        values = zvalues[sortedIndices[0:10]]
        weights = numpy.exp(-numpy.power(distances,1.7))/(numpy.mean(distances[0:3])**1.7)
        value = numpy.sum(weights*values)/numpy.sum(weights)
        return value
        '''
    return getValue
   
   
results = []

basedir = "llpScan_ctau1_llp2000_lsp1800"
   
for folderName in os.listdir(basedir):
    if folderName.startswith("signal_"):
        try:
            signalStrength = float(folderName.split("_")[1])
            results.append([signalStrength,os.path.join(basedir,folderName)])
        except:
            pass
results = sorted(results,key=lambda x: x[0])

mu1s = []
mu2s = []
llp1slo = []
llp2slo = []

llp1shi = []
llp2shi = []

#muLimit = 0.0024
muLimit = 0.0250

grid = {'logmu':[],'llpEff':[],'deltaNLL':[]}

for signalStrength,path in results:
    significance = getSigResult(os.path.join(path,"higgsCombineTest.Significance.mH120.root"))
    fitResult = getScanResult(os.path.join(path,"higgsCombineTest.MultiDimFit.mH120.root"))
    #print signalStrength,significance,fitResult["1s"][0]
    
    for i in range(len(fitResult['llpEff'])):
        grid['logmu'].append(math.log(signalStrength/muLimit))
        grid['llpEff'].append(fitResult['llpEff'][i])
        grid['deltaNLL'].append(fitResult['deltaNLL'][i])
    
    if fitResult["1s"][0]>0 and fitResult["1s"][1]>0:
        mu1s.append(signalStrength/muLimit)
        llp1slo.append(fitResult["1s"][0])
        llp1shi.append(fitResult["1s"][1])
    if fitResult["2s"][0]>0 and fitResult["2s"][1]>0:
        mu2s.append(signalStrength/muLimit)
        llp2slo.append(fitResult["2s"][0])
        llp2shi.append(fitResult["2s"][1])
        
deltaNLLfct = interpolate(grid)

mu1s = numpy.array(mu1s)
mu2s = numpy.array(mu2s)
llp1slo = numpy.array(llp1slo)
llp1shi = numpy.array(llp1shi)
llp2slo = numpy.array(llp2slo)
llp2shi = numpy.array(llp2shi)

graph1slo = ROOT.TGraph(len(mu1s),mu1s,llp1slo)
graph1shi = ROOT.TGraph(len(mu1s),mu1s,llp1shi)

graph2slo = ROOT.TGraph(len(mu2s),mu2s,llp2slo)
graph2shi = ROOT.TGraph(len(mu2s),mu2s,llp2shi)


cv = ROOT.TCanvas("cv","",800,670)

cvxmin=0.14
cvxmax=0.82
cvymin=0.135
cvymax=0.93

cv.SetLeftMargin(cvxmin)
cv.SetRightMargin(1-cvxmax)
cv.SetTopMargin(1-cvymax)
cv.SetBottomMargin(cvymin)

#cv.SetGridx(True)
#cv.SetGridy(True)

cv.SetLogx(1)

xBinning = numpy.logspace(math.log10(mu1s[0]),math.log10(100),151)
yBinning = numpy.linspace(0.2,1.5,151)

axis = ROOT.TH2F("axis",";;",
    len(xBinning)-1,xBinning,
    len(yBinning)-1,yBinning
)

axis.GetXaxis().SetTitle("#mu#kern[-0.6]{ }#lower[0.05]{#scale[1.1]{/}}#mu#lower[0.3]{#scale[0.7]{Limit}}")
axis.GetYaxis().SetTitle("Tagging efficiency SF")
axis.GetZaxis().SetTitle("-2#kern[-0.5]{ }#Delta#kern[-0.6]{ }ln(L)")

axis.GetXaxis().SetTickLength(0.015/(1-cvxmin-(1-cvxmax)))
axis.GetYaxis().SetTickLength(0.015/(1-cvymin-(1-cvymax)))
axis.GetZaxis().SetTickLength(0.015/(1-cvymin-(1-cvymax)))
axis.GetYaxis().SetNdivisions(512)

for ibin in range(axis.GetNbinsX()):
    mu = axis.GetXaxis().GetBinCenter(ibin+1)
    print mu
    for jbin in range(axis.GetNbinsY()):
        llpEff = axis.GetYaxis().GetBinCenter(jbin+1)
        deltaNLL = deltaNLLfct(math.log(mu),llpEff)
        #print mu,llpEff,deltaNLL
        axis.SetBinContent(ibin+1,jbin+1,deltaNLL)

axis.Draw("colz")
axis.GetZaxis().SetRangeUser(0,8)

color1s = newColorHLS(0.75,0.0,0.0)
color2s = newColorHLS(0.77,0.0,0.0)

graph1slo.SetLineColor(color1s.GetNumber())
graph1slo.SetLineWidth(2)

graph1shi.SetLineColor(color1s.GetNumber())
graph1shi.SetLineWidth(2)

graph1slo.Draw("L")
graph1shi.Draw("L")


graph2slo.SetLineColor(color2s.GetNumber())
graph2slo.SetLineWidth(3)
graph2slo.SetLineStyle(2)

graph2shi.SetLineColor(color2s.GetNumber())
graph2shi.SetLineWidth(3)
graph2shi.SetLineStyle(2)

graph2slo.Draw("L")
graph2shi.Draw("L")

effLine = ROOT.TLine(mu1s[0],1,100,1)
effLine.SetLineColor(1)
effLine.SetLineWidth(1)
effLine.SetLineStyle(1)
effLine.Draw("L")

limitLine = ROOT.TLine(1,axis.GetYaxis().GetXmin(),1,axis.GetYaxis().GetXmax())
limitLine.SetLineColor(1)
limitLine.SetLineWidth(1)
limitLine.SetLineStyle(2)
limitLine.Draw("L")

pTextCMS = ROOT.TPaveText(cv.GetLeftMargin(),1-cv.GetTopMargin()+0.055,cv.GetLeftMargin(),1-cv.GetTopMargin()+0.055,"NDC")
pTextCMS.AddText("CMS")
pTextCMS.SetTextFont(63)
pTextCMS.SetTextSize(32)
pTextCMS.SetTextAlign(13)
pTextCMS.Draw("Same")

pTextPreliminary = ROOT.TPaveText(cv.GetLeftMargin()+0.09,1-cv.GetTopMargin()+0.055,cv.GetLeftMargin()+0.09,1-cv.GetTopMargin()+0.055,"NDC")
pTextPreliminary.AddText("Simulation")
pTextPreliminary.SetTextFont(53)
pTextPreliminary.SetTextSize(32)
pTextPreliminary.SetTextAlign(13)
pTextPreliminary.Draw("Same")

pInfo = ROOT.TPaveText(1-cv.GetRightMargin(),1-cv.GetTopMargin()+0.06,1-cv.GetRightMargin(),1-cv.GetTopMargin()+0.06,"NDC")
pInfo.AddText("p#kern[-0.6]{ }p#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }#tilde{g}#kern[-0.6]{ }#tilde{g}, #tilde{g}#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }q#kern[-0.6]{ }#bar{q}#kern[-0.6]{ }#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}")
pInfo.SetTextFont(43)
pInfo.SetTextSize(32)
pInfo.SetTextAlign(33)
pInfo.Draw("Same")

legend = ROOT.TLegend(1-cv.GetRightMargin()-0.04-0.17,cv.GetBottomMargin()+0.03+0.15,1-cv.GetRightMargin()-0.04,cv.GetBottomMargin()+0.07)
legend.SetFillStyle(0)
legend.SetBorderSize(0)
legend.SetTextFont(43)
legend.SetTextSize(30)
legend.AddEntry(graph1shi,"68#kern[-0.6]{ }% CL","L")
legend.AddEntry(graph2shi,"95#kern[-0.6]{ }% CL","L")
legend.Draw("Same")
    
#ROOT.gPad.RedrawAxis()

cv.Print("llpscan.pdf")
cv.Print("llpscan.png")

cv.WaitPrimitive()

