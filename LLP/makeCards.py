import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json
import argparse
import math
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)


def getHist(fileName, histName):
    rootFile = ROOT.TFile(fileName)
    hist = rootFile.Get(histName)
    hist = hist.Clone()
    hist.SetDirectory(0)
    rootFile.Close()
    return hist

parser = argparse.ArgumentParser()

parser.add_argument("--path", default="/home/hep/vc1117/LLP/histo/hists_merged")
args = parser.parse_args()
hist_path = args.path

years = ["2016"] # ["2016", "2017", "2018"]
couplings = [2, 7, 12, 47, 52, 67]
#couplings = range(2, 68)

# make a datacard for a single HNL mass/coupling scenario
def make_datacard(cats, cats_signal, signal_name, output_path, coupling=12):
    for year in years:
        cb = ch.CombineHarvester()
        bkgs_mc = ["ttbar"]
        bkgs_abcd = ["qcd", "wjets", "dyjets"]
        signal = ["HNL"]

        cb.AddProcesses(era=[year], procs=bkgs_mc, bin=cats, signal=False)
        cb.AddProcesses(era=[year], procs=signal, bin=cats_signal, signal=True) # for now no signal outside region D

        if os.path.exists(output_path):
            print("Overwriting path!")
        else:
            os.makedirs(output_path)

        systematics = ["jesTotal", "jer", "pu", "trigger", "tight_muon_iso", "tight_muon_id", "tight_electron_id"]

        for syst in systematics:
            cb.cp().AddSyst(cb, syst, "shape", ch.SystMap()(1.0))

        cb.cp().AddSyst(cb, "lumi_$ERA", "lnN", ch.SystMap("era")([year], 1.026))


        cb.cp().signals().ExtractShapes(
                "{}/{}_{}.root".format(hist_path, signal_name, year),
                "$BIN/$PROCESS_coupling_{}".format(coupling),
                "$BIN/$PROCESS_coupling_{}_$SYSTEMATIC".format(coupling)
                )

        cb.cp().backgrounds().ExtractShapes(
                "{}/{}.root".format(hist_path, year),
                "$BIN/$PROCESS",
                "$BIN/$PROCESS_$SYSTEMATIC"
                )


        bbFactory = ch.BinByBinFactory()
        bbFactory.SetAddThreshold(0.1)
        #bbFactory.SetMergeThreshold(0.5)
        bbFactory.SetFixNorm(True)
        bbFactory.SetPattern("bb_$BIN_$PROCESS_bin_$#")
        #bbFactory.MergeBinErrors(cb.cp().backgrounds())
        bbFactory.AddBinByBin(cb.cp().backgrounds(), cb)
                
        shape_hist = getHist(
            os.path.join(hist_path, "{}.root".format(year)),
            "mumu_OS_prompt_D/ttbar"
        )

        nbins = shape_hist.GetNbinsX()
        bin_min = -0.5
        bin_max = nbins-0.5

        
        # pseudo-data
        for _, category_name in cats:
            obs = ch.Observation()
            for i, bkg in enumerate(bkgs_mc+bkgs_abcd):
                bkg_obs_hist = getHist(
                    os.path.join(hist_path,"{}.root".format(year)),
                        "{}/{}".format(category_name, bkg)
                )
                if i == 0:
                    obs_sum_hist = bkg_obs_hist.Clone(category_name)
                else:
                    obs_sum_hist.Add(bkg_obs_hist)

            obs_sum_hist.SetDirectory(0)
            obs.set_shape(obs_sum_hist,True)
            obs.set_bin(category_name)
            obs.set_era(year)
            cb.InsertObservation(obs)

        # ABCD method
        for _, category_name in cats_signal:
            for region in ["A","B","C", "D"]:
                name = category_name.replace("_D", "_"+region)
                for ibin in range(nbins):
                    proc = ch.Process()
                    process_name = "bkg_{}_bin{}".format(name, ibin+1)
                    syst_name = "rate_bkg_{}_bin{}".format(name, ibin+1)

                    proc.set_process(process_name)
                    proc.set_bin(name)
                    proc.set_era(year)

                    hist = ROOT.TH1F("bkgHist_{}_bin{}".format(name,ibin+1), "", nbins, bin_min, bin_max)
                    hist.SetBinContent(ibin+1, 1)
                    hist.SetBinError(ibin+1, 1e-9)
                    hist.SetDirectory(0)
                    proc.set_shape(hist, True)
                    cb.InsertProcess(proc)


                    if "_D" in process_name:
                        syst_name_A = category_name.replace("_D", "_A")
                        syst_name_B = category_name.replace("_D", "_B")
                        syst_name_C = category_name.replace("_D", "_C")

                        cb.cp().process([process_name]).bin([name]).AddSyst(cb, syst_name,"rateParam",
                            ch.SystMap("era")(["13TeV2016"],(
                            "TMath::Max(@0,0.000001)*TMath::Range(0,10.,TMath::Max(@1,0.000001)/TMath::Max(@2,0.000001))",
                            syst_name_A+","+syst_name_C+","+syst_name_B
                        ))
                        )       
                    else:
                        cb.cp().process([process_name]).bin([name]).AddSyst(cb, syst_name, "rateParam", ch.SystMap("era")([year], 1.))
                        param = cb.GetParameter(syst_name)

                        # Sum up all bkgs in mc to set initial param value
                        for i, bkg in enumerate(bkgs_mc):
                            bkg_hist = getHist(
                                os.path.join(hist_path,"{}.root".format(year)),
                                    "{}/{}".format(name, bkg)
                            )
                            if i == 0:
                                bkg_hist_sum = bkg_hist.Clone(name)
                            else:
                                bkg_hist_sum.Add(bkg_hist)

                        content = max(0.,bkg_hist_sum.GetBinContent(ibin+1))
                        err = max(0.,math.sqrt(bkg_hist_sum.GetBinContent(ibin+1)))
                        param.set_val(content)
                        param.set_range(0, 2*content+3*err)

        #cb.PrintAll()
        f = ROOT.TFile.Open(os.path.join(output_path, "out.root"), "RECREATE")

        cb.cp().WriteDatacard(
            os.path.join(output_path, "out.txt"),
            f
        )

        f.Close()
        return True


categories = [
    "mumu_OS_displaced",
    "mumu_SS_displaced",
    "ee_OS_displaced",
    "ee_SS_displaced",
    "mue_OS_displaced",
    "mue_SS_displaced",
    "emu_OS_displaced",
    "emu_SS_displaced",
    "mumu_OS_prompt",
    "mumu_SS_prompt",
    "ee_OS_prompt",
    "ee_SS_prompt",
    "mue_OS_prompt",
    "mue_SS_prompt",
    "emu_OS_prompt",
    "emu_SS_prompt",
    #"e",
    #"mu",
]

n_categories = len(categories)

category_pairs = []
category_pairs_signal = []

for index1, category_name in enumerate(categories):
    for index2, region in enumerate(["A", "B", "C", "D"]):
        index = index1*4 + index2 
        name = category_name+"_"+region
        pair=(index, name)
        if region == "D":
            category_pairs_signal.append(pair)
        category_pairs.append(pair)

n_job = 0
for proc in os.listdir(hist_path):
    if "HNL" not in proc:
        continue
    for year in years:
        if year not in proc:
            continue
        for coupling in couplings:
            n_job+=1

submit_file = open("runCombine.sh","w")
submit_file.write('''#!/bin/bash
#$ -cwd
#$ -q hep.q
#$ -l h_rt=00:05:00
#$ -e log/log.$TASK_ID.err
#$ -o log/log.$TASK_ID.out
#$ -t 1-'''+str(n_job)+'''
hostname
date
source ~/.cms_setup.sh
eval `scramv1 runtime -sh`
''')

submit_file.write("JOBS=(\n")
icounter = 0
for proc in os.listdir(hist_path):
    if "HNL" not in proc:
        continue
    for year in years:
        if year not in proc:
            continue
        for coupling in couplings:
            # parse name
            name = proc.replace("_{}.root".format(year), "")
            path = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}'.format(year, coupling, name))
            if make_datacard(category_pairs, category_pairs_signal, name, os.path.join(path), coupling=coupling):
                submit_file.write(" \"")
                submit_file.write('''combineTool.py -M AsymptoticLimits -t -1 --cminPreScan --cminPreFit 1 --rAbsAcc 0.000001 --run expected --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 -d %s/out.txt --there -n HNL --mass %i''' % (path, coupling))
                submit_file.write("\"")
                icounter += 1
                print("Done "+str(icounter)+"/"+str(n_job))
    #break

submit_file.write(")")
submit_file.write("\n")
submit_file.write("echo ${JOBS[$SGE_TASK_ID-1]}")
submit_file.write("\n")
submit_file.write("${JOBS[$SGE_TASK_ID-1]}")
submit_file.close()
