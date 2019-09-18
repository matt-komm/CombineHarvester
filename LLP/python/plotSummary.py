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
ROOT.gStyle.SetTitleOffset(1.3, "X")
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
ROOT.gStyle.SetLineStyleString(12,"7 6")

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
    
def interpol(xval,yval,xnew):
    fct = scipy.interpolate.interp1d(numpy.log10(xval), yval, kind='cubic')
    ynew = fct(numpy.log10(xnew))
    return ynew
    
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


SUS_16_038 = {
    'ctau_values':numpy.linspace(-6,2,9),
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
mgSymbol = "m#lower[0.2]{#scale[0.8]{"+gSymbol+"}}"
chiSymbol = "#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}"
mchiSymbol = "m#lower[0.2]{#scale[0.8]{"+chiSymbol+"}}"
    
    
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
ctauValue = {
    #"0p001":0,
    "0p01":-5,
    "0p1":-4,
    "1":-3,
    "10":-2,
    "100":-1,
    "1000":0,
    "10000":1,
}



with open("limits_da/summary.json") as f:
    data = json.load(f)
limitsC = data["compressed"]
limitsU = data["uncompressed"]

with open("limits_noda/summary.json") as f:
    data = json.load(f)
limitsCnoda = data["compressed"]
limitsUnoda = data["uncompressed"]


xvalues = []
yvaluesC = []
yvaluesU = []

yvaluesCnoda = []
yvaluesUnoda = []

yvaluesCexpUp = []
yvaluesUexpUp = []
yvaluesCexpDown= []
yvaluesUexpDown = []

yvaluesCtheoUp = []
yvaluesUtheoUp = []
yvaluesCtheoDown= []
yvaluesUtheoDown = []

yvaluesC_SUS = []
yvaluesU_SUS = []

for ctau in ctauValues:
    xvalues.append(10**ctauValue[ctau])
    yvaluesC.append(limitsC[ctau]["mean"])
    yvaluesU.append(limitsU[ctau]["mean"])
    
    yvaluesCnoda.append(limitsCnoda[ctau]["mean"])
    yvaluesUnoda.append(limitsUnoda[ctau]["mean"])
    
    yvaluesCexpUp.append(limitsC[ctau]["expUp"])
    yvaluesUexpUp.append(limitsU[ctau]["expUp"])
    yvaluesCexpDown.append(limitsC[ctau]["expDown"])
    yvaluesUexpDown.append(limitsU[ctau]["expDown"])
    
    yvaluesCtheoUp.append(limitsC[ctau]["theoUp"])
    yvaluesUtheoUp.append(limitsU[ctau]["theoUp"])
    yvaluesCtheoDown.append(limitsC[ctau]["theoDown"])
    yvaluesUtheoDown.append(limitsU[ctau]["theoDown"])
    
    sus_index = numpy.argmin(numpy.abs(SUS_16_038["ctau_values"]-ctauValue[ctau]))
    yvaluesC_SUS.append(SUS_16_038['exp']['dm_100']['mgl'][sus_index]/1000.)
    yvaluesU_SUS.append(SUS_16_038['exp']['mchi_100']['mgl'][sus_index]/1000.)
    
    print ctau,limitsC[ctau]["mean"],limitsU[ctau]["mean"]
    

xvalues = numpy.array(xvalues)
xvaluesRes = numpy.logspace(-5,1,50)
yvaluesC = numpy.array(yvaluesC)
yvaluesU = numpy.array(yvaluesU)

yvaluesCnoda = numpy.array(yvaluesCnoda)
yvaluesUnoda = numpy.array(yvaluesUnoda)


yvaluesCexpUp = interpol(xvalues,numpy.array(yvaluesCexpUp),xvaluesRes)
yvaluesUexpUp = interpol(xvalues,numpy.array(yvaluesUexpUp),xvaluesRes)
yvaluesCexpDown = interpol(xvalues,numpy.array(yvaluesCexpDown),xvaluesRes)
yvaluesUexpDown = interpol(xvalues,numpy.array(yvaluesUexpDown),xvaluesRes)


xvaluesSys = numpy.array(list(xvaluesRes)+list(reversed(list(xvaluesRes))))
yvaluesCexp = numpy.array(list(yvaluesCexpUp)+list(reversed(list(yvaluesCexpDown))))
yvaluesUexp = numpy.array(list(yvaluesUexpUp)+list(reversed(list(yvaluesUexpDown))))



yvaluesCtheo = numpy.array(yvaluesCtheoUp+list(reversed(yvaluesCtheoDown)))
yvaluesUtheo = numpy.array(yvaluesUtheoUp+list(reversed(yvaluesUtheoDown)))

yvaluesC_SUS = numpy.array(yvaluesC_SUS)
yvaluesU_SUS = numpy.array(yvaluesU_SUS)

rootObj = []

cvxmin = 0.135
cvxmax = 0.965
cvymin = 0.135
cvymax = 0.94

def makeCanvas(ymin=0,ymax=2.1):
    cv = ROOT.TCanvas("summary"+str(random.random()),"",800,670)
    #cv.SetGridx(True)
    #cv.SetGridy(True)
    #cv.SetLogx(1)
    #cv.SetMargin(0.155,0.04,0.15,0.065)

    #for the canvas:
    cv.SetBorderMode(0)
    cv.SetGridx(False)
    cv.SetGridy(False)

    #For the frame:
    cv.SetFrameBorderMode(0)
    cv.SetFrameBorderSize(1)
    cv.SetFrameFillColor(0)
    cv.SetFrameFillStyle(0)
    cv.SetFrameLineColor(1)
    cv.SetFrameLineStyle(1)
    cv.SetFrameLineWidth(1)

    # Margins:
    cv.SetLeftMargin(cvxmin)
    cv.SetRightMargin(1-cvxmax)

    # For the axis:
    cv.SetTickx(1)  # To get tick marks on the opposite side of the frame
    cv.SetTicky(1)

    # Change for log plots:
    cv.SetLogx(1)
    cv.SetLogy(0)
    cv.SetLogz(0)

    cv.SetTopMargin(1-cvymax)
    cv.SetBottomMargin(cvymin)

    cv.cd(1)
    axis1 = ROOT.TH2F("axis"+str(random.random()),";c#tau (m);95% CL lower limit on m #kern[-0.5]{ }#lower[0.2]{#scale[0.8]{#tilde{g}}} (TeV)",
        50,10**-5.2,10**1.2,
        50,ymin,ymax
    )
    axis1.GetXaxis().SetTickLength(0.017/(1-cv.GetLeftMargin()-cv.GetRightMargin()))
    axis1.GetYaxis().SetTickLength(0.015/(1-cv.GetTopMargin()-cv.GetBottomMargin()))
    axis1.Draw("AXIS")
    rootObj.append(axis1)
    
    return cv





colorU = newColorHLS(0.76,0.45,0.8)
colorUsys = newColorHLS(0.72,0.9,0.5)
colorU_SUS = newColorHLS(0.68,0.3,0.7)

colorC = newColorHLS(0.07,0.45,0.8)
colorCsys = newColorHLS(0.07,0.9,0.5)
colorC_SUS = newColorHLS(0.0,0.4,0.8)


polyCExp = ROOT.TPolyLine(len(xvaluesSys),xvaluesSys,yvaluesCexp)
polyCExp.SetFillColor(colorCsys.GetNumber())
polyCExp.SetFillStyle(1001)

polyUExp = ROOT.TPolyLine(len(xvaluesSys),xvaluesSys,yvaluesUexp)
polyUExp.SetFillColor(colorUsys.GetNumber())
polyUExp.SetFillStyle(1001)


graphC_SUS = ROOT.TGraph(len(xvalues),xvalues,yvaluesC_SUS)
graphC_SUS.SetLineColor(colorC_SUS.GetNumber())
graphC_SUS.SetLineWidth(3)
graphC_SUS.SetLineStyle(2)
graphC_SUS.SetMarkerStyle(24)
graphC_SUS.SetMarkerSize(2)
graphC_SUS.SetMarkerColor(colorC_SUS.GetNumber())

graphU_SUS = ROOT.TGraph(len(xvalues),xvalues,yvaluesU_SUS)
graphU_SUS.SetLineColor(colorU_SUS.GetNumber())
graphU_SUS.SetLineWidth(3)
graphU_SUS.SetLineStyle(2)
graphU_SUS.SetMarkerStyle(24)
graphU_SUS.SetMarkerSize(2)
graphU_SUS.SetMarkerColor(colorU_SUS.GetNumber())


yvaluesCRes = interpol(xvalues,yvaluesC,xvaluesRes)
graphC = ROOT.TGraph(len(xvaluesRes),xvaluesRes,yvaluesCRes)
graphC.SetLineColor(colorC.GetNumber())
graphC.SetLineWidth(2)
graphC.SetLineStyle(1)
graphC.SetMarkerStyle(20)
graphC.SetMarkerSize(1.7)
graphC.SetFillColor(colorCsys.GetNumber())
graphC.SetMarkerColor(colorC.GetNumber())

yvaluesCnodaRes = interpol(xvalues,yvaluesCnoda,xvaluesRes)
graphCnoda = ROOT.TGraph(len(xvaluesRes),xvaluesRes,yvaluesCnodaRes)
graphCnoda.SetLineColor(colorC.GetNumber())
graphCnoda.SetLineWidth(3)
graphCnoda.SetLineStyle(12)
graphCnoda.SetMarkerStyle(20)
graphCnoda.SetMarkerSize(1.7)
graphCnoda.SetFillColor(colorCsys.GetNumber())
graphCnoda.SetMarkerColor(colorC.GetNumber())

yvaluesURes = interpol(xvalues,yvaluesU,xvaluesRes)
graphU = ROOT.TGraph(len(xvaluesRes),xvaluesRes,yvaluesURes)
graphU.SetLineColor(colorU.GetNumber())
graphU.SetLineWidth(2)
graphU.SetLineStyle(1)
graphU.SetMarkerStyle(20)
graphU.SetMarkerSize(1.7)
graphU.SetFillColor(colorUsys.GetNumber())
graphU.SetMarkerColor(colorU.GetNumber())

yvaluesUnodaRes = interpol(xvalues,yvaluesUnoda,xvaluesRes)
graphUnoda = ROOT.TGraph(len(xvaluesRes),xvaluesRes,yvaluesUnodaRes)
graphUnoda.SetLineColor(colorU.GetNumber())
graphUnoda.SetLineWidth(3)
graphUnoda.SetLineStyle(12)
graphUnoda.SetMarkerStyle(20)
graphUnoda.SetMarkerSize(1.7)
graphUnoda.SetFillColor(colorUsys.GetNumber())
graphUnoda.SetMarkerColor(colorU.GetNumber())


graphC2 = ROOT.TGraph(len(xvalues),xvalues,yvaluesC)
graphC2.SetLineColor(colorC.GetNumber())
graphC2.SetLineWidth(2)
graphC2.SetLineStyle(1)
graphC2.SetMarkerStyle(20)
graphC2.SetMarkerSize(1.7)
graphC2.SetMarkerColor(colorC.GetNumber())

graphU2 = ROOT.TGraph(len(xvalues),xvalues,yvaluesU)
graphU2.SetLineColor(colorU.GetNumber())
graphU2.SetLineWidth(2)
graphU2.SetLineStyle(1)
graphU2.SetMarkerStyle(20)
graphU2.SetMarkerSize(1.7)
graphU2.SetMarkerColor(colorU.GetNumber())



pTextCMS = ROOT.TPaveText(cvxmin,cvymax+0.05,cvxmin,cvymax+0.05,"NDC")
pTextCMS.AddText("CMS")
pTextCMS.SetTextFont(63)
pTextCMS.SetTextSize(31)
pTextCMS.SetTextAlign(13)


pLumi = ROOT.TPaveText(cvxmax,cvymax+0.05,cvxmax,cvymax+0.05,"NDC")
pLumi.AddText("35.9 fb#lower[-0.8]{#scale[0.7]{-1}} (13 TeV)")
pLumi.SetTextFont(43)
pLumi.SetTextSize(31)
pLumi.SetTextAlign(33)

pInfo1 = ROOT.TPaveText(cvxmin+0.03,cvymax-0.04,cvxmin+0.03,cvymax-0.04-0.11,"NDC")
pInfo1.AddText("pp#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }"+gSymbol+"#kern[-0.6]{ }"+gSymbol+", "+gSymbol+"#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }q#kern[-0.7]{ }q#lower[-0.8]{#kern[-0.89]{#minus}}#kern[-0.6]{ }"+chiSymbol+"#kern[-0.8]{ }")
pInfo1.AddText(mgSymbol+"#kern[-0.2]{ }#minus#kern[-0.2]{ }"+mchiSymbol+" =#kern[-0.2]{ }100#kern[-0.4]{ }GeV")
pInfo1.SetTextFont(43)
pInfo1.SetTextSize(27)
pInfo1.SetTextAlign(11)

pInfo2 = ROOT.TPaveText(cvxmin+0.03,cvymax-0.02,cvxmin+0.03,cvymax-0.02,"NDC")
pInfo2.AddText("pp#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }"+gSymbol+"#kern[-0.6]{ }"+gSymbol+", "+gSymbol+"#kern[-0.5]{ }#rightarrow#kern[-0.5]{ }q#kern[-0.7]{ }q#lower[-0.8]{#kern[-0.89]{#minus}}#kern[-0.6]{ }"+chiSymbol+"#kern[-0.8]{ }, "+mchiSymbol+" =#kern[-0.2]{ }100#kern[-0.4]{ }GeV")
pInfo2.SetTextFont(43)
pInfo2.SetTextSize(27)
pInfo2.SetTextAlign(13)

legend1 = ROOT.TLegend(cvxmin+0.03,cvymin+0.03+0.17,cvxmin+0.03+0.45,cvymin+0.03)
legend1.SetFillStyle(0)
legend1.SetBorderSize(0)
legend1.SetTextFont(43)
legend1.SetTextSize(27)
legend1.AddEntry(graphC,"Displaced jet tagger","PLF")
legend1.AddEntry(graphCnoda,"w/o DA","L")
legend1.AddEntry(graphC_SUS,"#scale[0.9]{#font[82]{arXiv:1802.02110}}","PL")

legend2 = ROOT.TLegend(cvxmin+0.03,cvymin+0.03+0.17,cvxmin+0.03+0.45,cvymin+0.03)
legend2.SetFillStyle(0)
legend2.SetBorderSize(0)
legend2.SetTextFont(43)
legend2.SetTextSize(27)
legend2.AddEntry(graphU,"Displaced jet tagger","PLF")
legend2.AddEntry(graphUnoda,"w/o DA","L")
legend2.AddEntry(graphU_SUS,"#scale[0.9]{#font[82]{arXiv:1802.02110}}","PL")


pTextPreliminary = ROOT.TPaveText(cvxmin+0.09,cvymax+0.05,cvxmin+0.09,cvymax+0.05,"NDC")
pTextPreliminary.AddText("Simulation")
pTextPreliminary.SetTextFont(53)
pTextPreliminary.SetTextSize(31)
pTextPreliminary.SetTextAlign(13)

cvU = makeCanvas(ymax=2.5)
polyUExp.Draw("F")
graphU.Draw("SameL")
graphU2.Draw("SameP")
graphUnoda.Draw("SameL")
graphU_SUS.Draw("SameLP")
pInfo1.Draw("Same")
legend2.Draw("Same")
pTextCMS.Draw("Same")
pTextPreliminary.Draw("Same")
pLumi.Draw("Same")

cvU.Print("summaryU.pdf")
cvU.Print("summaryU.C")
cvU.Print("summaryU.png")

pTextPreliminary = ROOT.TPaveText(cvxmin+0.09,cvymax+0.05,cvxmin+0.09,cvymax+0.05,"NDC")
pTextPreliminary.AddText("Simulation Preliminary")
pTextPreliminary.SetTextFont(53)
pTextPreliminary.SetTextSize(31)
pTextPreliminary.SetTextAlign(13)
pTextPreliminary.Draw("Same")

cvU.Print("summaryU_pas.pdf")
cvU.Print("summaryU_pas.C")
cvU.Print("summaryU_pas.png")







pTextPreliminary = ROOT.TPaveText(cvxmin+0.09,cvymax+0.05,cvxmin+0.09,cvymax+0.05,"NDC")
pTextPreliminary.AddText("Simulation")
pTextPreliminary.SetTextFont(53)
pTextPreliminary.SetTextSize(31)
pTextPreliminary.SetTextAlign(13)

cvC = makeCanvas(ymax=2.)
polyCExp.Draw("F")
graphC.Draw("SameL")
graphC2.Draw("SameP")
graphCnoda.Draw("SameL")
graphC_SUS.Draw("SameLP")
pInfo2.Draw("Same")
legend1.Draw("Same")
pTextCMS.Draw("Same")
pTextPreliminary.Draw("Same")
pLumi.Draw("Same")

cvC.Print("summaryC.pdf")
cvC.Print("summaryC.C")
cvC.Print("summaryC.png")

pTextPreliminary = ROOT.TPaveText(cvxmin+0.09,cvymax+0.05,cvxmin+0.09,cvymax+0.05,"NDC")
pTextPreliminary.AddText("Simulation Preliminary")
pTextPreliminary.SetTextFont(53)
pTextPreliminary.SetTextSize(31)
pTextPreliminary.SetTextAlign(13)
pTextPreliminary.Draw("Same")

cvC.Print("summaryC_pas.pdf")
cvC.Print("summaryC_pas.C")
cvC.Print("summaryC_pas.png")





