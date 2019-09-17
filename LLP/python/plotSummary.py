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
mgSymbol = "m#lower[0.2]{#scale[0.8]{#kern[-0.75]{ }"+gSymbol+"}}"
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


xvalues = []
yvaluesC = []
yvaluesU = []

yvaluesC_SUS = []
yvaluesU_SUS = []

for ctau in ctauValues:
    xvalues.append(10**ctauValue[ctau])
    yvaluesC.append(limitsC[ctau]["mean"])
    yvaluesU.append(limitsU[ctau]["mean"])
    
    sus_index = numpy.argmin(numpy.abs(SUS_16_038["ctau_values"]-ctauValue[ctau]))
    yvaluesC_SUS.append(SUS_16_038['exp']['dm_100']['mgl'][sus_index]/1000.)
    yvaluesU_SUS.append(SUS_16_038['exp']['mchi_100']['mgl'][sus_index]/1000.)
    
    print ctau,limitsC[ctau]["mean"],limitsU[ctau]["mean"]
    
xvalues = numpy.array(xvalues)
    
yvaluesC = numpy.array(yvaluesC)
yvaluesU = numpy.array(yvaluesU)

yvaluesC_SUS = numpy.array(yvaluesC_SUS)
yvaluesU_SUS = numpy.array(yvaluesU_SUS)

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
    50,10**-5.2,10**1.2,
    50,0.0,0.0+2.1
)
axis1.GetXaxis().SetTickLength(0.017/(1-cv.GetPad(1).GetLeftMargin()-cv.GetPad(1).GetRightMargin()))
axis1.GetYaxis().SetTickLength(0.015/(1-cv.GetPad(1).GetTopMargin()-cv.GetPad(1).GetBottomMargin()))
axis1.Draw("AXIS")

cv.cd(2)
axis2 = ROOT.TH2F("axis",";;95% CL lower limit on m#lower[0.2]{#scale[0.8]{#tilde{g}}} (TeV)",
    50,10**-5.2,10**1.2,
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

graphC_SUS = ROOT.TGraph(len(xvalues),xvalues,yvaluesC_SUS)
graphC_SUS.SetLineColor(colorC_SUS.GetNumber())
graphC_SUS.SetLineWidth(3)
graphC_SUS.SetLineStyle(2)
graphC_SUS.SetMarkerStyle(24)
graphC_SUS.SetMarkerSize(2)
graphC_SUS.SetMarkerColor(colorC_SUS.GetNumber())
graphC_SUS.Draw("PL")

graphC = ROOT.TGraph(len(xvalues),xvalues,yvaluesC)
graphC.SetLineColor(colorC.GetNumber())
graphC.SetLineWidth(2)
graphC.SetLineStyle(1)
graphC.SetMarkerStyle(20)
graphC.SetMarkerSize(1.7)
graphC.SetMarkerColor(colorC.GetNumber())
graphC.Draw("PL")

cv.cd(2)

graphU_SUS = ROOT.TGraph(len(xvalues),xvalues,yvaluesU_SUS)
graphU_SUS.SetLineColor(colorU_SUS.GetNumber())
graphU_SUS.SetLineWidth(3)
graphU_SUS.SetLineStyle(2)
graphU_SUS.SetMarkerStyle(24)
graphU_SUS.SetMarkerSize(2)
graphU_SUS.SetMarkerColor(colorU_SUS.GetNumber())
graphU_SUS.Draw("PL")

graphU = ROOT.TGraph(len(xvalues),xvalues,yvaluesU)
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




