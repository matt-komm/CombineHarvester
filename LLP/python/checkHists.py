import ROOT
import numpy
import os
import sys
import json
import random
import argparse
import math

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleOffset(1.4,"Y")

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--ctau', dest='ctau', type=str, help='Ctau value')
parser.add_argument('-i', dest='inputFile', type=str, help='Input root file')

args = parser.parse_args()

processes = ["ZNuNu",'st','ttbar',"WJets","ctau"+args.ctau+"_llp2000_lsp200","ctau"+args.ctau+"_llp2000_lsp1800"]
systematics = ["jes","jer","unclEn","pu","wjetsScale","ttbarScale","stScale","znunuScale","mistag"]
colors = [ROOT.kRed,ROOT.kOrange+7,ROOT.kGreen+1,ROOT.kGray+1,ROOT.kGreen+2,ROOT.kOrange+10,ROOT.kMagenta,ROOT.kAzure-4,ROOT.kGray+2]

def getHist(fileName,histName):
    rootFile = ROOT.TFile(fileName)
    hist = rootFile.Get(histName)
    if not hist:
        print "Hist '",histName,"' not found in file: ",fileName
    hist = hist.Clone(hist.GetName()+str(random.random()))
    hist.SetDirectory(0)
    rootFile.Close()
    return hist
    
    
def getGraphFromHist(fileName,histName,offset=0.5,color=ROOT.kBlack,marker=20):
    hist = getHist(fileName,histName)
    
    N = hist.GetNbinsX()
    xvalues = numpy.zeros(N)
    yvalues = numpy.zeros(N)
    err = numpy.zeros(N)
    
    for ibin in range(N):
        xvalues[ibin] = hist.GetXaxis().GetBinCenter(ibin+1)+(offset-0.5)*hist.GetBinWidth(ibin+1)
        yvalues[ibin] = hist.GetBinContent(ibin+1)
        err[ibin] = hist.GetBinError(ibin+1)


    g = ROOT.TGraphErrors(N,xvalues,yvalues,numpy.zeros(N),err)
    g.SetMaximum(max(yvalues))
    g.SetMinimum(min(yvalues))
    g.SetLineColor(color)
    g.SetMarkerStyle(marker)
    g.SetMarkerSize(1.3)
    g.SetMarkerColor(color)
    
    hist.SetLineColor(color)
    hist.SetFillColor(color)
    hist.SetFillStyle(0)
    hist.SetMarkerStyle(marker)
    hist.SetMarkerSize(1.3)
    hist.SetMarkerColor(color)
    
    return g,hist

for process in processes:
    cv = ROOT.TCanvas("cv"+process+str(random.random()),"",800,670)
    cv.Divide(1,11,0,0)
    cv.GetPad(1).SetPad(0,0,1,1)
    cv.GetPad(1).SetMargin(0.12,0.04,0.6,0.07)
    axes = []
    for i in range(2,12):
        cv.GetPad(i).SetPad(0,0,1,1)
        w = (1.-0.12-0.04)/5.
        h = (1.-0.08-0.47)/2.
        xmin = 0.12+((i-2)%5)*w
        xmax = 1-xmin-w+0.005
        ymin = 0.08+((i-2)/5)*h
        ymax = 1-ymin-h+0.05
        
        print i,xmin,xmax,ymin,ymax
        
        cv.GetPad(i).SetMargin(xmin,xmax,ymin,ymax)
        cv.GetPad(i).SetFillStyle(4000)
        cv.cd(i)

        axistest = ROOT.TH2F("axis"+str(random.random()),"",50,-0.5,6.5,50,-0.95,0.95)
        if (i-2)%5>=1:
            axistest.GetYaxis().SetLabelSize(0)
        else:
            axistest.GetYaxis().SetTitle("Variation")
        if (i-2)/5>=1:
            axistest.GetXaxis().SetLabelSize(0)
        axistest.GetYaxis().SetNdivisions(406)
        axes.append(axistest)
        axistest.Draw("AXIS")
        
        if (i-2)<len(systematics):
            ptext = ROOT.TPaveText(xmin,1-ymax+0.01,xmin,1-ymax+0.01,"NDC")
            ptext.SetTextAlign(11)
            ptext.SetTextFont(43)
            ptext.SetTextSize(22)
            ptext.AddText(systematics[i-2])
            ptext.Draw("Same")
            axes.append(ptext)
        else:
            ptext = ROOT.TPaveText(xmin,1-ymax+0.01,xmin,1-ymax+0.01,"NDC")
            ptext.SetTextAlign(11)
            ptext.SetTextFont(43)
            ptext.SetTextSize(22)
            ptext.AddText("MC stat")
            ptext.Draw("Same")
            axes.append(ptext)
        
    cv.cd(1)
    nominalGraph,nominalHist = getGraphFromHist(args.inputFile,"llpD_"+process,offset=0.5,color=ROOT.kBlack,marker=20)
    upGraphs = []
    downGraphs = []
    
    upHists = []
    downHists = []
    for isyst,syst in enumerate(systematics):
    
        offset = 0.4*(1+isyst)/len(systematics)
        
        upGraph,upHist = getGraphFromHist(args.inputFile,"llpD_"+process+"_"+syst+"Up",offset=0.5+offset,color=colors[isyst],marker=22)
        upGraphs.append(upGraph)
        upHists.append(upHist)
        
        downGraph,downHist = getGraphFromHist(args.inputFile,"llpD_"+process+"_"+syst+"Down",offset=0.5-offset,color=colors[isyst],marker=23)
        downGraphs.append(downGraph)
        downHists.append(downHist)
        
    
    
    ymin = min(map(lambda x: x.GetMinimum() if x.GetMinimum()>1e-3 else 1e10,[nominalHist]+upHists+downHists))
    ymax = max(map(lambda x: x.GetMaximum() if x.GetMaximum()>1e-2 else 1e-10,[nominalHist]+upHists+downHists))
    print ymin,ymax
    axis = ROOT.TH2F("axis"+process+str(random.random()),";Binned P(LLP);Events", 
        50,-0.5,6.5,
        50,10**(math.log10(ymin)-0.15*(math.log10(ymax)-math.log10(ymin))),10**(math.log10(ymax)+0.15*(math.log10(ymax)-math.log10(ymin)))
    )
    cv.GetPad(1).SetLogy(1)
    axis.Draw("AXIS")
    nominalGraph.Draw("SamePE")
    for isyst,syst in enumerate(systematics):
        upGraphs[isyst].Draw("SamePE")
        downGraphs[isyst].Draw("SamePE")
        
        
    ratioHists = []
    for isyst,syst in enumerate(systematics):
        cv.cd(isyst+2)
        
        ratioUpHist = upHists[isyst].Clone(upHists[isyst].GetName()+str(random.random()))
        ratioHists.append(ratioUpHist)
        ratioUpHist.Add(nominalHist,-1)
        ratioUpHist.Divide(nominalHist)
        ratioUpHist.Draw("HISTPSame")
        
        ratioDownHist = downHists[isyst].Clone(downHists[isyst].GetName()+str(random.random()))
        ratioHists.append(ratioDownHist)
        ratioDownHist.Add(nominalHist,-1)
        ratioDownHist.Divide(nominalHist)
        ratioDownHist.Draw("HISTPSame")
        
    ratioUpHist = nominalHist.Clone(nominalHist.GetName()+str(random.random()))
    ratioHists.append(ratioUpHist)
    ratioDownHist = nominalHist.Clone(nominalHist.GetName()+str(random.random()))
    ratioHists.append(ratioDownHist)
    
    for ibin in range(ratioUpHist.GetNbinsX()):
        ratioUpHist.SetBinContent(ibin+1,nominalHist.GetBinError(ibin+1)/nominalHist.GetBinContent(ibin+1))
        ratioDownHist.SetBinContent(ibin+1,-nominalHist.GetBinError(ibin+1)/nominalHist.GetBinContent(ibin+1))
    
    cv.cd(11)
    ratioUpHist.SetMarkerStyle(22)
    ratioUpHist.SetMarkerSize(1.2)
    ratioUpHist.Draw("HISTPSame")
    ratioDownHist.SetMarkerStyle(23)
    ratioDownHist.SetMarkerSize(1.2)
    ratioDownHist.Draw("HISTPSame")
        
        
    ptext = ROOT.TPaveText(cv.GetPad(1).GetLeftMargin(),1-cv.GetPad(1).GetTopMargin()+0.02,cv.GetPad(1).GetLeftMargin(),1-cv.GetPad(1).GetTopMargin()+0.02,"NDC")
    ptext.SetTextAlign(11)
    ptext.SetTextFont(43)
    ptext.SetTextSize(25)
    ptext.AddText("Process: "+process)
    ptext.Draw("Same")
    
    cv.Print("syst_"+process+".pdf")
        
        
