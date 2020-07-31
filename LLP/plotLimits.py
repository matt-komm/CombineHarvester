import style
import ROOT
import json
from array import array
from scipy import optimize
import numpy as np
import math
import matplotlib.pyplot as plt

lumi = {"2016": 35.88, "2017": 41.53, "2018": 59.74}

def interpolatedTH2D(masses, couplings, values):
    log_couplings = np.log10(couplings)

    hist = ROOT.TH2D("", "", mass_range.size-1, mass_range,
                     coupling_range.size-1, coupling_range)

    graph = ROOT.TGraph2D(len(masses), array('d', masses),
                          array('d', log_couplings), array('d', values))
    graph.SetNpx(500)
    graph.SetNpy(500)
    interpolated_hist = graph.GetHistogram()

    for ibin in range(hist.GetNbinsX()+1):
        for jbin in range(hist.GetNbinsY()+1):
            mass = hist.GetXaxis().GetBinCenter(ibin+1)
            coupling = math.log10(hist.GetYaxis().GetBinCenter(jbin+1))
            xbin = interpolated_hist.GetXaxis().FindBin(mass)
            ybin = interpolated_hist.GetYaxis().FindBin(coupling)
            hist.SetBinContent(ibin+1, jbin+1,
                               interpolated_hist.GetBinContent(xbin, ybin))
    return hist

def fittedXsec(function, args):
    hist = ROOT.TH2D("", "", mass_range.size-1, mass_range,
                     coupling_range.size-1, coupling_range)

    for ibin in range(hist.GetNbinsX()+1):
        for jbin in range(hist.GetNbinsY()+1):
            mass = hist.GetXaxis().GetBinCenter(ibin+1)
            coupling = (hist.GetYaxis().GetBinCenter(jbin+1))
            hist.SetBinContent(ibin+1, jbin+1, coupling*function(mass, *args))
    return hist    



def findExclusion(hist1, hist2):
    hist = hist1.Clone()
    hist.Divide(hist2)
    graph = ROOT.TGraph()
    i = 0
    for ibin in range(hist.GetNbinsX()+1):
        limit_min = 1.
        y_min = 0.1
        x = hist.GetXaxis().GetBinCenter(ibin)
        for jbin in range(hist.GetNbinsY()+1):
            if hist.GetBinContent(ibin+1, jbin+1) < 1. and hist.GetBinContent(ibin+1, jbin+1) > 0.:
                y = hist.GetYaxis().GetBinCenter(jbin)
                if y < y_min:
                    y_min = y
        if y_min != 0.1:
            graph.SetPoint(i, x, y_min)
            i += 1
    graph.SetLineWidth(2)
    return graph
# store information in dictionaries

# open store theory cross-sections and expected limits

'''
matthias_points_mass = []
matthias_points_couplings = []
with open('points.txt') as f:
    for l in f:
        matthias_points_mass.append(float(l.strip().split(" ")[1]))
        matthias_points_couplings.append(float(l.strip().split(" ")[2])**2)
print(matthias_points_mass, matthias_points_couplings)
matthias_points = ROOT.TGraph(len(matthias_points_mass), np.asarray(matthias_points_mass), np.asarray(matthias_points_couplings))
matthias_points.SetMarkerColor(ROOT.kBlue)
'''

with open('xsec.json') as f:
    xsecDict = json.load(f)
for year in ["2016"]:

    with open("limitDict"+year+".json") as f:
        limitDict = json.load(f)
    log_coupling_range = np.arange(-8, -0.5, step=0.1)
    #mass_range = np.arange(1, 20.5, step=0.25)
    mass_range = np.arange(1, 10.5, step=0.25)
    coupling_range = np.power(10, log_coupling_range)


    preds = {}
    npoints = len(limitDict)
    for point, results in limitDict.items():
        fragments = point.split('_')
        mass = float(fragments[5].replace('massHNL', '').replace('p', '.'))
        preds[mass] = []

    for point, results in limitDict.items():
        fragments = point.split('_')
        mass = float(fragments[5].replace('massHNL', '').replace('p', '.'))
        coupling = float(fragments[6].replace('Vall', '').replace('p', '.'))
        coupling *= coupling
        print(mass, coupling)
        preds[mass].extend([{coupling: results}])

    masses = []
    couplings = []
    exp_limits = []

    for mass, coupling_dicts in preds.items():
        for coupling_dict in coupling_dicts:
            for coupling, result in coupling_dict.items():
                expected = result["exp0"]
                masses.append(mass)
                couplings.append(coupling)
                exp_limits.append(expected)

    used_points_graph = ROOT.TGraph(len(masses), array('d', masses),
                                    array('d', couplings))
    used_points_graph.SetMarkerColor(ROOT.kBlue)
    limit_hist = interpolatedTH2D(masses, couplings, exp_limits)


    masses = []
    couplings = []
    xsecs = []

    for mass, coupling_dicts in xsecDict.items():
        for coupling_dict in coupling_dicts:
            for coupling, result in coupling_dict.items():
                xsec = result["xsec"]
                masses.append(float(mass))
                couplings.append(float(coupling))
                xsecs.append(xsec)
    all_points_graph = ROOT.TGraph(len(masses), array('d', masses),
                                   array('d', couplings))

    xsec_over_coupling = np.divide(xsecs, couplings)
    def fit_func(x, a, b, c, d):
        #print(x)
        #print(b*x)
        #print(np.multiply(x, x))
        return a * (1. + np.multiply(b, x) + c * np.power(x, 2) + d * np.power(x, 3))

    params, params_covariance = optimize.curve_fit(fit_func, masses, xsec_over_coupling,
                                                   p0=[5000, 0.1, 0.001, 0.0001])

    xsec_hist = fittedXsec(fit_func, params)
    exclusion_graph = findExclusion(limit_hist, xsec_hist)
    cv = style.makeCanvas()
    cv.Draw("")

    cv.SetLogy()
    cv.SetLogx()
    cv.SetLogz()
    limit_hist.GetXaxis().SetTitle("m_{N} (GeV)")
    limit_hist.GetYaxis().SetTitle("|V_{\muN}|^{2}")
    limit_hist.GetZaxis().SetTitle("95% CL expected limit #sigma (pb) #bullet B(W#rightarrow q#bar{q})")
    limit_hist.GetZaxis().SetRangeUser(1e-3, 1e3)   

    limit_hist.Draw("COLZ")
    used_points_graph.Draw("PSAME")
    #matthias_points.Draw("PSAME")
    exclusion_graph.Draw("LSAME")

    leg = style.makeLegend(0.6, 0.7, 0.4, 0.9)
    leg.AddEntry(exclusion_graph, "exclusion", "l")
    leg.AddEntry(used_points_graph, "Matthias points", "p")
    #leg.AddEntry(matthias_points, "Matthias' points", "p")
    leg.Draw("SAME")
    style.makeCMSText(0.17, 0.95, additionalText="Simulation Preliminary")
    style.makeLumiText(0.9, 0.95, year=year, lumi=lumi[year])
    cv.SaveAs("test"+year+".pdf")

    xsec_hist.GetXaxis().SetTitle("m_{N} (GeV)")
    xsec_hist.GetYaxis().SetTitle("|V_{\muN}|^{2}")
    xsec_hist.GetZaxis().SetTitle("theory \sigma (pb) \cdot BR")
    xsec_hist.GetZaxis().SetRangeUser(1e-7, 1e3)   
    xsec_hist.Draw("COLZ")
    all_points_graph.Draw("LSAME")
    cv.SaveAs("xsec.pdf")
