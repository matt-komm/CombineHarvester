import style
import ROOT
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

    # arrays to store mass, V2 and sigma/sigma_th values

    masses = []
    couplings = []
    sigma_ratios = []

    for year in years:
        for f in os.listdir("./"):
            if ".json" not in f:
                continue

            # limit json aggreggate 
            with open(f) as json_file:
                xsecDict = json.load(json_file)
            if str(scenario) not in xsecDict.keys():
                continue
            xsecDict = xsecDict[str(scenario)]

            # means something failed with combine (shouldn't happend!)
            if "exp0" not in xsecDict:
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
            expected = xsecDict["exp0"]

            ratio = expected/xsec

            masses.append(mass)
            couplings.append(coupling)
            sigma_ratios.append(ratio)

        # draw 1d exclusion plots for each mass point
        df = pd.DataFrame(list(zip(masses, couplings, sigma_ratios)), 
                       columns =['mass', 'coupling', 'ratio'])
        #print(df)

        mass_list = sorted(df.mass.unique())
        sensitive_masses = []
        crossing_points = []
        print("list of masses to be analyzed", mass_list)


        # make 1d plot and find crossing point
        for mass in mass_list:
            coupling_df = df.loc[df['mass'] == mass].sort_values('coupling')
            ratio_df = coupling_df.sort_values('ratio')

            couplings = array('d', coupling_df.coupling)
            ratios = array('d', coupling_df.ratio)

            tgr = ROOT.TGraph(len(couplings), couplings, ratios)

            l = ROOT.TLine(couplings[0], 1, couplings[-1], 1)
            l.SetLineStyle(2)

            cv = style.makeCanvas()
            cv.SetLogx()
            cv.SetLogy()
            cv.Draw("")
            tgr.GetXaxis().SetTitle("|V_{lN}|^2")
            tgr.GetYaxis().SetTitle("#frac{#sigma}{#sigma_{th}}")
            tgr.Draw("APC")
            l.Draw("SAME")

            # sigma_UL = sigma_th
            xx = ratio_df.ratio
            yy = ratio_df.coupling
            logx = np.log10(xx)
            logy = np.log10(yy)
            lin_interp = interpolate.interp1d(logx, logy, kind="linear")


            try:
                crossing_point = np.power(10.0, lin_interp(0))
            except ValueError:
                print("Could not interpolate!")
            else:
                crossing_points.append(crossing_point)
                sensitive_masses.append(mass)
                print(crossing_point)
                l_crossing = ROOT.TLine(crossing_point, sorted(ratios)[0], crossing_point, sorted(ratios)[-1])
                l_crossing.SetLineStyle(3)
                l_crossing.Draw("SAME")
            cv.SaveAs("limit_coupling_{}_mass_{}_year_{}.pdf".format(scenario, mass, year))

        graph = ROOT.TGraph(len(crossing_points), array('d', sensitive_masses), array('d', crossing_points))

        cv = style.makeCanvas()
        cv.Draw("")
        cv.SetLogy()
        cv.SetLogx()
        graph.Draw("")
        graph.GetXaxis().SetTitle("m_{N} (GeV)")
        graph.GetYaxis().SetTitle("|V_{lN}|^{2}")

        graph.GetXaxis().SetLimits(1, 20.)
        graph.SetMinimum(1e-7)
        graph.SetMaximum(1e-1)
        leg = style.makeLegend(0.6, 0.7, 0.4, 0.9)
        leg.Draw("SAME")
        style.makeText(0.2, 0.8, 0.2, 0.8, coupling_title)
        style.makeCMSText(0.17, 0.95, additionalText="Simulation Preliminary")
        style.makeLumiText(0.9, 0.95, year=year, lumi=lumi[year])
        cv.SaveAs("limit_coupling_{}_{}.pdf".format(scenario, year))
