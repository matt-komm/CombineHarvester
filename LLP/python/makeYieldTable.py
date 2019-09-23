import ROOT
import numpy
import os
import sys
import json
import random
import argparse
import math
import scipy.interpolate

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTitleOffset(1.4,"Y")

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--ctau', dest='ctau', type=str, help='Ctau value',required=True)
parser.add_argument('-i', dest='inputFile', type=str, help='Input root file',required=True)

args = parser.parse_args()

processes = ["ZNuNu",'st','ttbar',"WJets","ctau"+args.ctau+"_llp2000_lsp0","ctau"+args.ctau+"_llp1600_lsp1400"]
systematics = ["jes","jer","unclEn","pu","wjetsScale","ttbarScale","stScale","znunuScale","mistag"]
colors = [ROOT.kRed,ROOT.kOrange+7,ROOT.kGreen+1,ROOT.kGray+1,ROOT.kGreen+2,ROOT.kOrange+10,ROOT.kMagenta,ROOT.kAzure-4,ROOT.kGray+2]

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

def getHist(fileName,histName):
    rootFile = ROOT.TFile(fileName)
    hist = rootFile.Get(histName)
    if not hist:
        print "Hist '",histName,"' not found in file: ",fileName
    hist = hist.Clone(hist.GetName()+str(random.random()))
    hist.SetDirectory(0)
    rootFile.Close()
    return hist
    
def roundToSig(value,err):
    ndigits = int(math.log10(err))-1
    if ndigits>0:
        errClip = (int(round(err))/10**ndigits)*10**ndigits
        valueClip = (int(round(value))/10**ndigits)*10**ndigits
        return valueClip,errClip
    return value,err

    
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
    
nominalHists = {}
upHists = {}
downHists = {}

xsecFct = getTheoryXsecFct("theory_xsec.dat")
xsec_mg2000,_,_ = xsecFct(2000.)
xsec_mg1600,_,_ = xsecFct(1600.)

for process in processes:
    nominalGraph,nominalHist = getGraphFromHist(args.inputFile,"llpD_"+process,offset=0.5,color=ROOT.kBlack,marker=20)
    if process.find("llp2000")>=0:
        nominalHist.Scale(xsec_mg2000)
    elif process.find("llp1600")>=0:
        nominalHist.Scale(xsec_mg1600)
    nominalHists[process] = nominalHist
    upHists[process] = {}
    downHists[process] = {}

    for isyst,syst in enumerate(systematics):
        upGraph,upHist = getGraphFromHist(args.inputFile,"llpD_"+process+"_"+syst+"Up")
        if process.find("llp2000")>=0:
            upHist.Scale(xsec_mg2000)
        elif process.find("llp1600")>=0:
            upHist.Scale(xsec_mg1600)
        upHists[process][syst] = upHist
        
        downGraph,downHist = getGraphFromHist(args.inputFile,"llpD_"+process+"_"+syst+"Down")
        if process.find("llp2000")>=0:
            downHist.Scale(xsec_mg2000)
        elif process.find("llp1600")>=0:
            downHist.Scale(xsec_mg1600)
        downHists[process][syst] = downHist
        

sumBkg = [0. for _ in range(7)]
sumBkgerr = [1e-10 for _ in range(7)]

for process in ["ZNuNu",'st','ttbar',"WJets"]:
    print process,
    for ibin in range(1,7):
        n = nominalHists[process].GetBinContent(ibin+1)
        mcstat = nominalHists[process].GetBinError(ibin+1)
        
        expUp = (mcstat/n-1)**2
        expDown = (mcstat/n-1)**2
        expAvg = (mcstat/n-1)**2
        for syst in systematics:
            u = upHists[process][syst].GetBinContent(ibin+1)
            d = downHists[process][syst].GetBinContent(ibin+1)
            expUp += max(u/n-1,d/n-1)**2
            expDown += min(u/n-1,d/n-1)**2
            expAvg += 0.25*((u/n-1)**2+(d/n-1)**2)
        
        sumBkg[ibin] += n
        sumBkgerr[ibin] += expAvg*n**2
        
        if n>0.1:
            if n>100:
                print "&   $%7.0f$ & $%-7.0f$"%(roundToSig(n,math.sqrt(expAvg)*n)),
            else:
                print "&   $%7.1f$ & $%-7.1f$"%(roundToSig(n,math.sqrt(expAvg)*n)),
        else:
            print "& \\multicolumn{2}{c}{$<0.1$}",

    print "\\\\"
    
print "total background",
for ibin in range(1,7):
    if sumBkg[ibin]>0.1:
        if sumBkg[ibin]>100.:
            print "&   $%7.0f$ & $%-7.0f$"%(roundToSig(sumBkg[ibin],math.sqrt(sumBkgerr[ibin]))),
        else:
            print "&   $%7.1f$ & $%-7.1f$"%(roundToSig(sumBkg[ibin],math.sqrt(sumBkgerr[ibin]))),
    else:
        print "& \\multicolumn{2}{c}{$<0.1$}",

print "\\\\"
    
    
for process in ["ctau"+args.ctau+"_llp2000_lsp0","ctau"+args.ctau+"_llp1600_lsp1400"]:
    print process,
    for ibin in range(1,7):
        n = nominalHists[process].GetBinContent(ibin+1)
        mcstat = nominalHists[process].GetBinError(ibin+1)
        
        expUp = (mcstat/n-1)**2
        expDown = (mcstat/n-1)**2
        expAvg = (mcstat/n-1)**2
        for syst in systematics:
            u = upHists[process][syst].GetBinContent(ibin+1)
            d = downHists[process][syst].GetBinContent(ibin+1)
            expUp += max(u/n-1,d/n-1)**2
            expDown += min(u/n-1,d/n-1)**2
            expAvg += 0.25*((u/n-1)**2+(d/n-1)**2)
        
        sumBkg[ibin] += n
        sumBkgerr[ibin] += expAvg*n
        
        if n>0.1:
            if n>100:
                print "&   $%7.0f$ & $%-7.0f$"%(roundToSig(n,math.sqrt(expAvg)*n)),
            else:
                print "&   $%7.1f$ & $%-7.1f$"%(roundToSig(n,math.sqrt(expAvg)*n)),
        else:
            print "& \\multicolumn{2}{c}{$<0.1$}",

    print "\\\\"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
