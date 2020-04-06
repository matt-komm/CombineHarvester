import style
import ROOT
import json
from array import array
from scipy.interpolate import bisplrep, bisplev
import numpy as np


# open store theory cross-sections and expected limits
with open('limitDict.json') as f:
    limitDict = json.load(f)


with open('/vols/build/cms/LLP/HNL_xsec.json') as f:
    xsecDict = json.load(f)


def interpolatedTH2D(masses, couplings, values):
    # construct a spline to interpolate
    couplings = np.log10(couplings)
    # m, log10(v^2), value
    # limit_spline = bisplrep(masses, couplings, values, kx=2, ky=2, s=0.1)
    interpolation = bisplrep(masses, couplings, values, kx=3, ky=3, quiet=0, s=0.2)
    coupling_range = np.arange(-10, -0.5, step=0.5)
    log_coupling_range = np.power(10, coupling_range)
    mass_range = np.arange(1, 20.5, step=0.5)

    # interpolated_limits = bisplev(mass_range, coupling_range, limit_spline)
    interpolated_limits = bisplev(mass_range, coupling_range, interpolation)
    grid_hist = ROOT.TH2D("", "", mass_range.size-1, mass_range, log_coupling_range.size-1, log_coupling_range)
    for ibin in range(grid_hist.GetNbinsX()+1):
        for jbin in range(grid_hist.GetNbinsY()+1):
            grid_hist.SetBinContent(ibin, jbin, interpolated_limits[ibin,jbin])
    return grid_hist


# store information in dictionaries

preds = {}
npoints = len(limitDict)
for point, results in limitDict.items():
    fragments = point.split('-')
    mass = float(fragments[1].split('_')[0])
    preds[mass] = []

for point, results in limitDict.items():
    fragments = point.split('-')
    mass = float(fragments[1].split('_')[0])
    coupling = fragments[2].replace('_', '.').replace('e', '')
    if len(fragments) > 3:
        exponent = "e-"+fragments[3]
    else:
        exponent = "e0"
    coupling = float(coupling+exponent)
    coupling *= coupling
    preds[mass].extend([{coupling: results}])


masses = []
couplings = []
exp_limits = []

for mass, coupling_dicts in preds.items():
    for coupling_dict in coupling_dicts:
        for coupling, result in coupling_dict.items():
            expected = result["exp0"]
            if expected < 1:
                masses.append(mass)
                couplings.append(coupling)
                exp_limits.append(expected)
grid_hist = interpolatedTH2D(np.array(masses), np.array(couplings), np.array(exp_limits))
used_points_graph = ROOT.TGraph(len(masses), array('d', masses), array('d', couplings))

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

xsec_hist = interpolatedTH2D(np.array(masses), np.array(couplings), np.array(xsecs))
points_graph = ROOT.TGraph(len(masses), array('d', masses), array('d', couplings))

cv = style.makeCanvas()
cv.Draw("")
cv.SetBottomMargin(0.12)
cv.SetLeftMargin(0.15)
cv.SetRightMargin(0.2)

cv.SetLogy()
cv.SetLogz()
grid_hist.GetXaxis().SetTitle("m_{N} (GeV)")
grid_hist.GetYaxis().SetTitle("|V_{\muN}|^{2}")
grid_hist.GetZaxis().SetTitle("95% CL expected limit \sigma (pb)")
grid_hist.GetZaxis().SetRangeUser(1e-3, 1)   


#div_hist = grid_hist.Clone()
#div_hist.Divide(xsec_hist)


grid_hist.Draw("COLZtext")
used_points_graph.Draw("SAMEP")
#div_hist.Draw("COLZ")
cv.SaveAs("test.pdf")

xsec_hist.GetZaxis().SetRangeUser(1e-6, 10)
xsec_hist.Draw("COLZtext")
points_graph.Draw("SAMEP")

#fit xsec hist
cv.SaveAs("xsec.pdf")