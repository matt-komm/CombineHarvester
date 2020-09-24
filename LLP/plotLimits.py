import style
import ROOT
ROOT.gROOT.SetBatch(1)
import json
from array import array
from scipy import interpolate
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import os
import yaml

'''
HNL_majorana_all_ctau1p0e00_massHNL1p0_Vall5p274e-01
     02 fractions=1.000,0.000,0.000 => couplings=8.0064e-01,0.0000e+00,0.0000e+00
     07 fractions=0.500,0.500,0.000 => couplings=5.7204e-01,5.7204e-01,0.0000e+00
     12 fractions=0.000,1.000,0.000 => couplings=0.0000e+00,8.1759e-01,0.0000e+00
     47 fractions=0.500,0.000,0.500 => couplings=6.9015e-01,0.0000e+00,6.9015e-01
     52 fractions=0.000,0.500,0.500 => couplings=0.0000e+00,7.0092e-01,7.0092e-01
     67 fractions=0.000,0.000,1.000 => couplings=0.0000e+00,0.0000e+00,1.3615e+00
'''

with open("/vols/build/cms/LLP/gridpackLookupTable.json") as lookup_table_file:
    lookup_table = json.load(lookup_table_file)



lumi = {"2016": 35.88, "2017": 41.53, "2018": 59.74}
years = ["2016"]
couplings = [2.0, 7.0, 12.0, 47.0, 52.0, 67.0]
coupling_dict = {}
coupling_dict[2.0] = ["ee", "U_{e} : U_{#mu} : U_{#tau} = 1 : 0 : 0"]
coupling_dict[7.0] = ["emu", "U_{e} : U_{#mu} : U_{#tau} = 1 : 1 : 0"]
coupling_dict[12.0] = ["mumu", "U_{e} : U_{#mu} : U_{#tau} = 0 : 1 : 0"]
coupling_dict[47.0] = ["etau", "U_{e} : U_{#mu} : U_{#tau} = 1 : 0 : 1"]
coupling_dict[52.0] = ["mutau", "U_{e} : U_{#mu} : U_{#tau} = 0 : 1 : 1"]
coupling_dict[67.0] = ["tautau", "U_{e} : U_{#mu} : U_{#tau} = 0 : 0 : 1"]

mass_range = np.arange(1, 20.5, step=0.5)
log_coupling_range = np.arange(-8, -0.5, step=0.1)
coupling_range = np.power(10, log_coupling_range)

for scenario in couplings:
    print("Analyzing coupling scenario: "+str(scenario))
    coupling_text = coupling_dict[scenario][0]
    coupling_title = coupling_dict[scenario][1]

    for hnl_type in ["majorana", "dirac"]:
        print(hnl_type)
        # arrays to store mass, V2 and sigma/sigma_th values
        masses = []
        couplings = []
        sigma_ratios = {}
        for exp_var in ["exp0", "exp+1", "exp+2", "exp-1", "exp-2"]:
            sigma_ratios[exp_var] = []

        for year in years:
            for f in os.listdir("./"):
                if ".json" not in f:
                    continue

                if hnl_type not in f:
                    continue

                # limit json aggreggate 
                with open(f) as json_file:
                    xsecDict = json.load(json_file)
                if str(scenario) not in xsecDict.keys():
                    continue
                xsecDict = xsecDict[str(scenario)]

                # means something failed with combine (shouldn't happend!)
                if "exp0" not in xsecDict or "exp+1" not in xsecDict or "exp+2" not in xsecDict or "exp-1" not in xsecDict or "exp-2" not in xsecDict:
                    continue

                # parse lookup table
                proc = f.replace("limits_", "").replace(".json", "")
                lu_infos = lookup_table[proc]['weights'][str(int(scenario))]
                xsec = lu_infos['xsec']['nominal']
                coupling = lu_infos['couplings']['Ve']+lu_infos['couplings']['Vmu']+lu_infos['couplings']['Vtau']
                if coupling not in (2, 12, 67):
                    coupling = coupling/2

                coupling = coupling ** 2
                mass = lookup_table[proc]['mass']

                for exp_var in ["exp0", "exp+1", "exp+2", "exp-1", "exp-2"]:
                    expected = xsecDict[exp_var]
                    ratio = expected/xsec
                    sigma_ratios[exp_var].append(ratio)

                masses.append(mass)
                couplings.append(coupling)

            # draw 1d exclusion plots for each mass point
            df = pd.DataFrame(list(zip(masses, couplings, sigma_ratios["exp0"], sigma_ratios["exp+1"], sigma_ratios["exp+2"], sigma_ratios["exp-1"], sigma_ratios["exp-2"])), 
                           columns =['mass', 'coupling', 'exp0', 'exp+1', 'exp+2', 'exp-1', 'exp-2'])
            #print(df)

            mass_list = sorted(df.mass.unique())
            sensitive_masses = {}
            crossing_points = {}
            for exp_var in ["exp0", "exp+1", "exp+2", "exp-1", "exp-2"]:
                crossing_points[exp_var] = []
                sensitive_masses[exp_var] = []
            print("list of masses to be analyzed", mass_list)


            # make 1d plot and find crossing point
            for mass in mass_list:
                coupling_df = df.loc[df['mass'] == mass].sort_values('coupling')
                ratio_df = coupling_df.sort_values('exp0')
                couplings = array('d', coupling_df.coupling)

                if len(couplings) < 2:
                    print "need at least 2 points to interpolate!"
                    continue

                for exp_var in sigma_ratios.keys():
                    ratios = array('d', coupling_df[exp_var])
                    tgr = ROOT.TGraph(len(couplings), couplings, ratios)
                    # sigma_UL = sigma_th
                    xx = ratio_df[exp_var]
                    yy = ratio_df.coupling
                    logx = np.log10(xx)
                    logy = np.log10(yy)
                    lin_interp = interpolate.interp1d(logx, logy, kind="linear")

                    try:
                        crossing_point = np.power(10.0, lin_interp(0))
                    except ValueError:
                        print("Could not interpolate!")
                    else:
                        crossing_points[exp_var].append(crossing_point)
                        sensitive_masses[exp_var].append(mass)
                        if exp_var == "exp0":
                            l_crossing = ROOT.TLine(crossing_point, sorted(ratios)[0], crossing_point, sorted(ratios)[-1])
                            l_crossing.SetLineStyle(3)

                    if exp_var == "exp0":
                        cv = style.makeCanvas()
                        cv.SetLogx()
                        cv.SetLogy()
                        cv.Draw("")
                        tgr.GetXaxis().SetTitle("|V_{lN}|^2")
                        tgr.GetYaxis().SetTitle("#frac{#sigma}{#sigma_{th}}")
                        tgr.Draw("APC")
                        l = ROOT.TLine(couplings[0], 1, couplings[-1], 1)
                        l.SetLineStyle(2)
                        l.Draw("SAME")
                        l_crossing.Draw("SAME")
                        cv.SaveAs("limit_{}_coupling_{}_mass_{}_year_{}.pdf".format(hnl_type, scenario, mass, year))

        print(crossing_points["exp+1"], crossing_points["exp0"])
        y_error_up = [y_up-y for y_up, y in zip(crossing_points["exp+1"], crossing_points["exp0"])]
        y_error_down = [y-y_down for y_down, y in zip(crossing_points["exp-1"], crossing_points["exp0"])]
        print(y_error_up)
        x = np.zeros(len(crossing_points["exp0"]))

        if hnl_type == "majorana":
            #graph_majorana = ROOT.TGraph(len(crossing_points["exp0"]), array('d', sensitive_masses["exp0"]), array('d', crossing_points["exp0"]))
            graph_majorana = ROOT.TGraphAsymmErrors(len(crossing_points["exp0"]), array('d', sensitive_masses["exp0"]), array('d', crossing_points["exp0"]), array('d', x), array('d', x), array('d', y_error_up), array('d', y_error_down))
        else:
            graph_dirac = ROOT.TGraphAsymmErrors(len(crossing_points["exp0"]), array('d', sensitive_masses["exp0"]), array('d', crossing_points["exp0"]), array('d', x), array('d', x), array('d', y_error_up), array('d', y_error_down))

    cv = style.makeCanvas()
    cv.Draw("")
    cv.SetLogy()
    cv.SetLogx()
    graph_majorana.Draw("ACP3")
    graph_majorana.GetXaxis().SetTitle("m_{N} (GeV)")
    graph_majorana.GetYaxis().SetTitle("|V_{lN}|^{2}")

    graph_majorana.GetXaxis().SetLimits(1, 20.)
    graph_majorana.SetMinimum(1e-7)
    graph_majorana.SetMaximum(1e-1)

    graph_majorana.SetLineColor(ROOT.kAzure)
    graph_majorana.SetMarkerColor(ROOT.kAzure)
    graph_majorana.SetFillColorAlpha(ROOT.kAzure, 0.3)
    graph_dirac.SetLineColor(ROOT.kOrange)
    graph_dirac.SetMarkerColor(ROOT.kOrange)
    graph_dirac.SetFillColorAlpha(ROOT.kOrange, 0.3)

    graph_dirac.Draw("SAMECP3")
    leg = style.makeLegend(0.65, 0.75, 0.8, 0.87)
    leg.AddEntry(graph_majorana, "Majorana", "lpf")
    leg.AddEntry(graph_dirac, "Dirac", "lpf")
    leg.Draw("SAME")
    style.makeText(0.2, 0.8, 0.2, 0.8, coupling_title)
    style.makeCMSText(0.17, 0.95, additionalText="Simulation Preliminary")
    style.makeLumiText(0.9, 0.95, year=year, lumi=lumi[year])
    cv.SaveAs("limit_coupling_{}_{}.pdf".format(scenario, year))
