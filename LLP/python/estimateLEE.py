import os
import sys
import numpy
import math
import ROOT
import random
import json
import uproot
import re
import scipy
import scipy.interpolate

# ROOT.gStyle.SetHistFillStyle(0)
# ROOT.gStyle.SetLegoInnerR(Float_t rad = 0.5)
# ROOT.gStyle.SetNumberContours(Int_t number = 20)
ROOT.gROOT.SetBatch(True)
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

ROOT.gStyle.SetHatchesSpacing(1)
ROOT.gStyle.SetHatchesLineWidth(2)

# ROOT.gStyle.SetStaROOT.TStyle(Style_t style = 1001)
# ROOT.gStyle.SetStatX(Float_t x = 0)
# ROOT.gStyle.SetStatY(Float_t y = 0)


#ROOT.gROOT.ForceStyle(True)
#end modified

# For the Global title:

ROOT.gStyle.SetOptTitle(0)



# ROOT.gStyle.SetTitleH(0) # Set the height of the title box
# ROOT.gStyle.SetTitleW(0) # Set the width of the title box
#ROOT.gStyle.SetTitleX(0.35) # Set the position of the title box
#ROOT.gStyle.SetTitleY(0.986) # Set the position of the title box
# ROOT.gStyle.SetTitleStyle(Style_t style = 1001)
#ROOT.gStyle.SetTitleBorderSize(0)

# For the axis titles:
ROOT.gStyle.SetTitleColor(1, "XYZ")
ROOT.gStyle.SetTitleFont(43, "XYZ")
ROOT.gStyle.SetTitleSize(35, "XYZ")
# ROOT.gStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
# ROOT.gStyle.SetTitleYSize(Float_t size = 0.02)
ROOT.gStyle.SetTitleXOffset(1.2)
#ROOT.gStyle.SetTitleYOffset(1.2)
ROOT.gStyle.SetTitleOffset(1.45, "Y") # Another way to set the Offset
ROOT.gStyle.SetTitleOffset(1.38, "Z")
# For the axis labels:

ROOT.gStyle.SetLabelColor(1, "XYZ")
ROOT.gStyle.SetLabelFont(43, "XYZ")
ROOT.gStyle.SetLabelOffset(0.0077, "XYZ")
ROOT.gStyle.SetLabelSize(29, "XYZ")
#ROOT.gStyle.SetLabelSize(0.04, "XYZ")

ROOT.gStyle.SetGridColor(ROOT.kBlack)
ROOT.gStyle.SetGridStyle(2)
ROOT.gStyle.SetGridWidth(1)

# For the axis:

ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetAxisColor(1, "XYZ")
ROOT.gStyle.SetStripDecimals(True)
ROOT.gStyle.SetTickLength(0.025, "Y")
ROOT.gStyle.SetTickLength(0.025, "X")


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
ROOT.gStyle.SetPaperSize(8.5*1.4,7.0*1.4)
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

ROOT.gStyle.SetPaintTextFormat("3.0f")

NRGBs = 7;
NCont = 255;

stops = numpy.array( [0.0,0.15, 0.4, 0.55,0.65, 0.88, 1.00] )
red  = numpy.array( [0.6,0.00, 0.00,0.3, 0.87, 1.00, 0.51] )
green = numpy.array( [0.0,0.00, 0.81,0.8, 1.00, 0.20, 0.00] )
blue = numpy.array( [0.8,0.51, 1.00,0.1, 0.12, 0.00, 0.00] )

colWheelDark = ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)

for i in range(NRGBs):
    red[i]=min(1,red[i]*1.1+0.25)
    green[i]=min(1,green[i]*1.1+0.25)
    blue[i]=min(1,blue[i]*1.1+0.25)

colWheel = ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
ROOT.gStyle.SetNumberContours(NCont)
'''

NRGBs = 3;
NCont = 8;

stops = numpy.array( [0.0, 0.5, 1.00] )
red  = numpy.array( [0.05,  0.1,  0.95] )
green = numpy.array( [0.35, 0.95,  0.75] )
blue = numpy.array( [0.95,  0.75, 0.05] )

colWheelDark = ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)


colWheel = ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
ROOT.gStyle.SetNumberContours(NCont)

'''
'''
stops = numpy.array( [0.00, 0.20, 0.4, 0.6, 0.8, 1.00] )
red  = numpy.array( [163/255., 123/255.,  96/255., 145/255., 221/255., 253/255.] )
green = numpy.array( [33/255.,  77/255., 180/255., 242/255., 223/255., 217/255.] )
blue = numpy.array([254./255., 251/255., 237/255., 180/255., 165/255., 209/255.] )
colWheel = ROOT.TColor.CreateGradientColorTable(6, stops, red, green, blue, 255)
ROOT.gStyle.SetNumberContours(255)
'''
ROOT.gRandom.SetSeed(123)

colors=[]
def hex2rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16)/255.0 for i in range(0, lv, lv // 3))

def newColor(red,green,blue):
    newColor.colorindex+=1
    color=ROOT.TColor(newColor.colorindex,red,green,blue)
    colors.append(color)
    return color
    
newColor.colorindex=301

def getDarkerColor(color):
    darkerColor=newColor(color.GetRed()*0.6,color.GetGreen()*0.6,color.GetBlue()*0.6)
    return darkerColor

basePath = 'cards_new'

mglu = "m#lower[0.2]{#scale[0.8]{#tilde{g}}}"
mchi = "m#lower[0.2]{#scale[0.8]{#tilde{#chi}#lower[-0.5]{#scale[0.65]{0}}#kern[-1.2]{#lower[0.6]{#scale[0.65]{1}}}}}"

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

for ctau in ctauLabels.keys():

    print ctau
    fileDictPerSeed = {}
    llpMasses = {}
    lspMasses = {}
    for folder in os.listdir(basePath):
        if re.match('ctau'+ctau+'_llp[0-9]+_lsp[0-9]+',folder):
            llpMass = int(folder[folder.find('llp')+3:folder.find('_',folder.find('llp'))])
            lspMass = int(folder[folder.find('lsp')+3:])
            
            for f in os.listdir(os.path.join(basePath,folder)):
                if re.match('higgsCombineTest.Significance.mH120.[0-9]+.root',f):
                    if not fileDictPerSeed.has_key(f):
                        fileDictPerSeed[f] = []
                        llpMasses[f] = []
                        lspMasses[f] = []
                    fileDictPerSeed[f].append(os.path.join(basePath,folder,f))
                    llpMasses[f].append(llpMass)
                    lspMasses[f].append(lspMass)
    
    histSig = ROOT.TH1F("sig"+ctau,"",100,-0.0001,3)
    xmin = 0.600
    xmax = 2.500
    ymin = 0.0
    ymax = 2.500
    histMasses = ROOT.TH2F("masses"+ctau,";LLP (TeV); LSP (Tev)",
        int(round((xmax-xmin)/0.050))+1,xmin-0.025,xmax+0.025,
        int(round((ymax-ymin)/0.050))+1,ymin-0.025,ymax+0.025
    )
    for k in fileDictPerSeed.keys():
        print k,len(fileDictPerSeed[k])
        sigPerPoint = []
        for f in fileDictPerSeed[k]:
            rootFile = uproot.open(f)
            if len(rootFile.keys())==0:
                print "WARNING - file '"+f+"' likely corrupted -> skip"
                continue
            sig = rootFile['limit']['limit'].array()
            #print f,numpy.sort(sig)[-5:]
            
            sigPerPoint.append(sig)
 
        sigPerPoint = numpy.stack(sigPerPoint,axis=0)
        
        
        maxIndex = numpy.argmax(sigPerPoint,axis=0)
        #maxIndex = numpy.ones(sigPerPoint.shape[1],dtype=numpy.int32)*0
        
        for i in range(maxIndex.shape[0]):
            histSig.Fill(sigPerPoint[maxIndex[i],i])
            histMasses.Fill(0.001*llpMasses[k][maxIndex[i]],0.001*lspMasses[k][maxIndex[i]],sigPerPoint[maxIndex[i],i])

    #print histSig.GetEntries(), histSig.Integral(2,histSig.GetNbinsX()+2)/histSig.GetEntries()
    histSig.Scale(1./histSig.GetEntries())
    histMasses.Scale(1./histSig.GetEntries()) #average max significance
    
    s = 0.99999
    
    localSig = numpy.zeros(histSig.GetNbinsX()+1)
    globalSig = numpy.zeros(histSig.GetNbinsX()+1)
    
    for ibin in range(histSig.GetNbinsX()+1):
        c = histSig.GetBinContent(ibin)
        localSig[ibin] = histSig.GetBinCenter(ibin)
        #globalSig[ibin] = 2*ROOT.TMath.ErfInverse(1.-s)/math.sqrt(2) if s<1 else 0
        globalSig[ibin] =  ROOT.RooStats.PValueToSignificance(s)
        #print ibin,localSig[ibin],globalSig[ibin],s
        histSig.SetBinContent(ibin,s)
        #histSig.SetBinError(ibin,math.sqrt(s*histSig.GetEntries())/histSig.GetEntries() if s>0 else 0)
        s-=c
    print s,histSig.GetBinContent(histSig.GetNbinsX()+1)
        
    cvSigMasses = ROOT.TCanvas("cvSigMasses"+ctau,"",800,700)
    cvSigMasses.SetMargin(0.155,0.24,0.15,0.09)
    histMasses.Draw("colz")
    cvSigMasses.Print("leeSigMasses_"+ctau+".pdf")
    cvSigMasses.Print("leeSigMasses_"+ctau+".png")

    cvSig = ROOT.TCanvas("cvSig"+ctau,"",800,700)
    cvSig.SetLogy(1)
    cvSig.SetGridx(True)
    cvSig.SetGridy(True)
    cvSig.SetMargin(0.155,0.04,0.15,0.09)
    axisSig = ROOT.TH2F("axisSig"+ctau,";Max. significance #forall ("+mglu+",#kern[-0.6]{ }"+mchi+");Normalized cumulative #toys",
        50,histSig.GetXaxis().GetXmin(),histSig.GetXaxis().GetXmax(),
        50,0.0001,1.1
    )
    axisSig.Draw("AXIS")
    histSig.SetLineColor(ROOT.kOrange+7)
    histSig.SetLineWidth(2)
    histSig.SetMarkerSize(0)
    histSig.SetMarkerStyle(0)
    #histSig.Draw("HISTLESame")
    histSig.Draw("HISTLSame")
    ROOT.gPad.RedrawAxis()
    
    pTextCMS = ROOT.TPaveText(cvSig.GetLeftMargin(),1-cvSig.GetTopMargin()*0.4,cvSig.GetLeftMargin(),1-cvSig.GetTopMargin()*0.4,"NDC")
    pTextCMS.AddText("CMS")
    pTextCMS.SetTextFont(63)
    pTextCMS.SetTextSize(32)
    pTextCMS.SetTextAlign(13)
    pTextCMS.Draw("Same")
    
    pTextPreliminary = ROOT.TPaveText(cvSig.GetLeftMargin()+0.1,1-cvSig.GetTopMargin()*0.4,cvSig.GetLeftMargin()+0.1,1-cvSig.GetTopMargin()*0.4,"NDC")
    pTextPreliminary.AddText("Preliminary")
    pTextPreliminary.SetTextFont(53)
    pTextPreliminary.SetTextSize(32)
    pTextPreliminary.SetTextAlign(13)
    pTextPreliminary.Draw("Same")
    
    pTextCTau = ROOT.TPaveText(1-cvSig.GetRightMargin(),1-cvSig.GetTopMargin()*0.4,1-cvSig.GetRightMargin(),1-cvSig.GetTopMargin()*0.4,"NDC")
    pTextCTau.AddText("c#tau#kern[-0.5]{ }=#kern[-0.8]{ }%s"%ctauLabels[ctau])
    pTextCTau.SetTextFont(43)
    pTextCTau.SetTextSize(32)
    pTextCTau.SetTextAlign(33)
    pTextCTau.Draw("Same")
    
    
    cvSig.Update()
    cvSig.Print("leeSig_"+ctau+".pdf")
    cvSig.Print("leeSig_"+ctau+".png")
    
    cvTF = ROOT.TCanvas("cvTF"+ctau,"",800,700)
    #cvTF.SetLogy(1)
    cvTF.SetGridx(True)
    cvTF.SetGridy(True)
    cvTF.SetMargin(0.155,0.04,0.15,0.09)
    axisTF = ROOT.TH2F("axisTF"+ctau,";Local significance;Global significance",50,0,3,50,0,3)
    axisTF.Draw("AXIS")
    gTF = ROOT.TGraph(localSig.shape[0],localSig,globalSig)
    gTF.SetLineColor(ROOT.kOrange+7)
    gTF.SetLineWidth(2)
    gTF.Draw("L")
    bisector = ROOT.TF1("bisector","x",0,6)
    bisector.SetLineColor(ROOT.kBlack)
    bisector.SetLineStyle(2)
    bisector.SetLineWidth(1)
    bisector.Draw("SameL")
    ROOT.gPad.RedrawAxis()
    
    pTextCMS = ROOT.TPaveText(cvTF.GetLeftMargin(),1-cvTF.GetTopMargin()*0.4,cvTF.GetLeftMargin(),1-cvTF.GetTopMargin()*0.4,"NDC")
    pTextCMS.AddText("CMS")
    pTextCMS.SetTextFont(63)
    pTextCMS.SetTextSize(32)
    pTextCMS.SetTextAlign(13)
    pTextCMS.Draw("Same")
    
    pTextPreliminary = ROOT.TPaveText(cvTF.GetLeftMargin()+0.1,1-cvTF.GetTopMargin()*0.4,cvTF.GetLeftMargin()+0.1,1-cvTF.GetTopMargin()*0.4,"NDC")
    pTextPreliminary.AddText("Preliminary")
    pTextPreliminary.SetTextFont(53)
    pTextPreliminary.SetTextSize(32)
    pTextPreliminary.SetTextAlign(13)
    pTextPreliminary.Draw("Same")
    
    pTextCTau = ROOT.TPaveText(1-cvTF.GetRightMargin(),1-cvTF.GetTopMargin()*0.4,1-cvTF.GetRightMargin(),1-cvTF.GetTopMargin()*0.4,"NDC")
    pTextCTau.AddText("c#tau#kern[-0.5]{ }=#kern[-0.8]{ }%s"%ctauLabels[ctau])
    pTextCTau.SetTextFont(43)
    pTextCTau.SetTextSize(32)
    pTextCTau.SetTextAlign(33)
    pTextCTau.Draw("Same")
    
    cvTF.Update()
    cvTF.Print("leeTF_"+ctau+".pdf")
    cvTF.Print("leeTF_"+ctau+".png")
    

