import matplotlib
matplotlib.use('Agg') 
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

def getGraph(fileName, histName):
    rootFile = ROOT.TFile(fileName)
    hist = rootFile.Get(histName)
    rootFile.Close()
    return hist

json_path = "jsons"

K_FACTOR = 1.1


with open("/vols/cms/LLP/gridpackLookupTable.json") as lookup_table_file:
    lookup_table = json.load(lookup_table_file)

limits_ghent = {}

lumi = {"2016": 35.9, "2017": 41.5, "2018": 59.7, "combined": 137.1}
years = ["2016", "2017", "2018", "combined"]

coupling_dict = {}
coupling_dict[2.0] = ["ee", "U_{e} : U_{#mu} : U_{#tau} = 1 : 0 : 0"]
coupling_dict[7.0] = ["emu", "U_{e} : U_{#mu} : U_{#tau} = 1 : 1 : 0"]
coupling_dict[12.0] = ["mumu", "U_{e} : U_{#mu} : U_{#tau} = 0 : 1 : 0"]
coupling_dict[47.0] = ["etau", "U_{e} : U_{#mu} : U_{#tau} = 1 : 0 : 1"]
coupling_dict[52.0] = ["mutau", "U_{e} : U_{#mu} : U_{#tau} = 0 : 1 : 1"]
#coupling_dict[67.0] = ["tautau", "U_{e} : U_{#mu} : U_{#tau} = 0 : 0 : 1"]

mass_range = np.arange(1, 24.5, step=0.5)
log_coupling_range = np.arange(-8, -0.5, step=0.1)
coupling_range = np.power(10, log_coupling_range)

for year in years:
    print(year)
    for scenario in coupling_dict.keys():
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

            for f in os.listdir(json_path):
                if year not in f:
                    continue
                if ".json" not in f:
                    continue
                if hnl_type not in f:
                    continue
                # limit json aggreggate 
                print(f)
                with open(os.path.join(json_path, f)) as json_file:
                    xsecDict = json.load(json_file)
                if str(scenario) not in xsecDict.keys():
                    continue
                xsecDict = xsecDict[str(scenario)]

                # means something failed with combine (shouldn't happend!)
                if "exp0" not in xsecDict or "exp+1" not in xsecDict or "exp+2" not in xsecDict or "exp-1" not in xsecDict or "exp-2" not in xsecDict:
                    continue

                # parse lookup table
                proc = f.replace(year+"_", "").replace("limits_", "").replace(".json", "")
                lu_infos = lookup_table[proc]['weights'][str(int(scenario))]
                xsec = lu_infos['xsec']['nominal']*K_FACTOR
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
            mass_points = np.array(df['mass'])
            coupling_points = np.array(df['coupling'])
            npoints = len(mass_points)
            if hnl_type == "majorana":
                points_graph = ROOT.TGraph(npoints, mass_points, coupling_points)
                points_graph.SetMarkerStyle(33)
                points_graph.SetMarkerSize(1)

            mass_list = sorted(df.mass.unique())
            sensitive_masses = {}
            for exp_var in ["exp0", "exp+1", "exp+2", "exp-1", "exp-2"]:
                sensitive_masses[exp_var] = {}
            print "list of masses to be analyzed {}".format(mass_list)


            # make 1d plot and find crossing point
            i = 0
            fig, ax = plt.subplots(figsize=(24, 18))
            fig.suptitle("{}, coupling scenario {}".format(hnl_type, scenario), size=40)
            for mass in mass_list:
                coupling_df = df.loc[df['mass'] == mass].sort_values('coupling')
                ratio_df = coupling_df.sort_values('exp0')
                couplings = array('d', coupling_df.coupling)

                if len(couplings) < 2:
                    print "need at least 2 points to interpolate!"
                    continue
                i += 1

                for exp_var in sigma_ratios.keys():
                    ratios = array('d', coupling_df[exp_var])
                    x = np.log10(couplings)
                    y = np.log10(ratios)

                    xrange = np.geomspace(1e-10, 1.)

                    coeffs = np.polyfit(x, y, 2)
                    poly = np.poly1d(coeffs)
                    
                    y_fitted = poly(np.log10(xrange))
                    roots = np.roots(coeffs)

                    def filter_root(root):
                        if root > -8 and root < 0. and np.imag(root) == 0 and root<max(x)+2 and root>min(x)-0.5:
                            return True
                        else:
                            return False

                    roots = filter(filter_root, roots)
                    roots = np.power(10, roots)

                    if len(roots) == 2:
                        roots = [roots[0]]
                    
                    if len(roots) == 1:
                        root_lower = roots[0]
                        sensitive_masses[exp_var][mass] = root_lower

                    if exp_var == "exp0":
                        plt.subplot(3, 4, i)
                        plt.xlabel(r'$|V_{lN}|^2$')
                        plt.ylabel(r'$\frac{\sigma}{\sigma_{th}}$') 
                        plt.xscale('log')
                        plt.yscale('log')
                        plt.title("{} GeV".format(mass))
                        plt.plot(couplings, ratios, 'o')
                        plt.plot(xrange, np.power(10, y_fitted))
                        plt.axhline(1.)
                        for root in roots:
                            plt.axvline(root)

            plt.savefig("limits/fit_{}_coupling_{}_year_{}.pdf".format(hnl_type, scenario, year))
            plt.clf()


            y_values = []
            y_values_down = []
            y_values_up = []
            masses = []

            for mass in mass_list:
                if mass not in sensitive_masses["exp0"]:
                    continue
                else:
                    masses.append(mass)
                    y = sensitive_masses["exp0"][mass]
                if mass in sensitive_masses["exp+1"]:
                    y_up = max(0, sensitive_masses["exp+1"][mass]-y)
                else:
                    y_up = 0.
                if mass in sensitive_masses["exp-1"]:
                    y_down = max(0, y-sensitive_masses["exp-1"][mass])
                
                y_values.append(y)
                y_values_down.append(y_down)
                y_values_up.append(y_up)

            n = len(y_values)
            x = np.zeros(n)
            masses = array('d', masses)
            y_values = array('d', y_values)
            y_values_down = array('d', y_values_down)
            y_values_up = array('d', y_values_up)

            if hnl_type == "majorana":
                graph_majorana = ROOT.TGraphAsymmErrors(n, masses, y_values, x, x, y_values_down, y_values_up)
                # if len(y_error_up_upper) == 0:
                #     upperMajorana = False
                # else:
                #     upperMajorana = True
                #     #graph_majorana_upper = ROOT.TGraphAsymmErrors(len(crossing_points_upper["exp0"]), array('d', sensitive_masses_upper["exp0"]), array('d', crossing_points_upper["exp0"]), array('d', x_upper), array('d', y_error_up_upper), array('d', y_error_down_upper))

            else:
                graph_dirac = ROOT.TGraphAsymmErrors(n, masses, y_values, x, x, y_values_down, y_values_up)
                # if len(y_error_up_upper) == 0:
                #     upperDirac = False
                # else:
                #     upperDirac = True
                #     #graph_dirac_upper = ROOT.TGraphAsymmErrors(len(crossing_points_upper["exp0"]), array('d', sensitive_masses_upper["exp0"]), array('d', crossing_points_upper["exp0"]), array('d', x_upper), array('d', y_error_up_upper), array('d', y_error_down_upper))

        cv = style.makeCanvas()
        cv.Draw("")
        cv.SetLogy()
        cv.SetLogx()
        graph_majorana.Draw("ACP3")
        graph_majorana.GetXaxis().SetTitle("m_{N} (GeV)")
        graph_majorana.GetYaxis().SetTitle("|V_{lN}|^{2}")

        graph_majorana.GetXaxis().SetLimits(1, 20.)
        graph_majorana.SetMinimum(1e-7)
        graph_majorana.SetMaximum(1e3)
        graph_majorana.GetXaxis().SetMoreLogLabels()

        graph_majorana.SetLineColor(ROOT.kAzure)
        graph_majorana.SetMarkerColor(ROOT.kAzure)
        graph_majorana.SetFillColorAlpha(ROOT.kAzure, 0.3)

        graph_dirac.SetLineColor(ROOT.kOrange)
        graph_dirac.SetMarkerColor(ROOT.kOrange)
        graph_dirac.SetFillColorAlpha(ROOT.kOrange, 0.3)

        graph_dirac.Draw("SAMECP3")
        graph_majorana.Draw("SAME CP3")
        points_graph.Draw("SAME P")

        leg = style.makeLegend(0.16, 0.47, 0.5, 0.67)
        leg.AddEntry(graph_majorana, "Majorana", "lpf")
        leg.AddEntry(graph_dirac, "Dirac", "lpf")

        # Table 3: displaced HNL, Vmu , Dirac
        # Table 4: displaced HNL, Vmu, Majorana
        # Table 6: Prompt HNL, Vmu Dirac+Majorana
        # Table 5: prompt HNL, Ve Dirac+Majorana

        if scenario == 12:
            hist_displaced_dirac = getGraph("hepdata/HEPData-ins1736526-v1.root", "Table 3/Graph1D_y1")
            hist_displaced_majorana = getGraph("hepdata/HEPData-ins1736526-v1.root", "Table 4/Graph1D_y1")
            hist_prompt = getGraph("hepdata/HEPData-ins1736526-v1.root", "Table 6/Graph1D_y1")
            hist_displaced_dirac.SetLineColor(ROOT.kRed)
            hist_displaced_majorana.SetLineColor(ROOT.kBlue)
            hist_prompt.SetLineStyle(2)
            hist_displaced_dirac.SetLineWidth(2)
            hist_displaced_majorana.SetLineWidth(2)
            hist_prompt.SetLineWidth(2)

            hist_displaced_dirac.Draw("SAME")
            hist_displaced_majorana.Draw("SAME")
            hist_prompt.Draw("SAME")

            leg.AddEntry(hist_displaced_dirac, "ATLAS 3l, displaced LNC")
            leg.AddEntry(hist_displaced_majorana, "ATLAS 3l, displaced LNV")
            leg.AddEntry(hist_prompt, "ATLAS 3l, prompt")

        elif scenario == 2:
            hist_prompt = getGraph("hepdata/HEPData-ins1736526-v1.root", "Table 5/Graph1D_y1")
            hist_prompt.SetLineStyle(2)
            hist_prompt.SetLineWidth(2)
            hist_prompt.Draw("SAME")
            leg.AddEntry(hist_prompt, "ATLAS 3l, prompt")


        leg.Draw("SAME")
        style.makeText(0.18, 0.7, 0.2, 0.7, coupling_title)
        style.makeCMSText(0.18, 0.87, additionalText="Simulation Preliminary")
        style.makeLumiText(0.18, 0.8, year=year, lumi=lumi[year])
        cv.SaveAs("limits/limit_coupling_{}_{}.pdf".format(scenario, year))
