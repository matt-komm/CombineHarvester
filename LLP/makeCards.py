import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json

years = ["2016"] # ["2016", "2017", "2018"]
couplings = [2, 7, 12, 47, 52, 67]
couplings = range(2, 68)

hist_path = "/home/hep/vc1117/LLP/histo/hists_merged"

# make a datacard for a single HNL mass/coupling scenario
def make_datacard(cats, cats_signal, signal_name, output_path, coupling=12):
    for year in years:
        cb = ch.CombineHarvester()
        procs = ["qcd"] #["ttbar", "qcd", "wjets", "dyjets"]
        signal = ["HNL"]

        cb.AddProcesses(era=[year], procs=procs, bin=cats, signal=False)
        cb.AddProcesses(era=[year], procs=signal, bin=cats_signal, signal=True)

        if os.path.exists(output_path):
            print("Overwriting path!")
        else:
            os.makedirs(output_path)

        systematics = ["jesTotal", "jer", "pu", "trigger", "tight_muon_iso", "tight_muon_id", "tight_electron_id"]

        for syst in systematics:
            cb.cp().AddSyst(cb, syst, "shape", ch.SystMap()(1.0))

        cb.cp().AddSyst(cb, "lumi_$ERA", "lnN", ch.SystMap("era")([year], 1.026))

        try:
            cb.cp().signals().ExtractShapes(
                  "{}/{}_{}.root".format(hist_path, signal_name, year),
                  "$BIN/$PROCESS_coupling_{}".format(coupling),
                  "$BIN/$PROCESS_coupling_{}_$SYSTEMATIC".format(coupling)
                  )
        except RuntimeError:
            print("Got error. Skipping!")
            return False
        else:
            cb.cp().backgrounds().ExtractShapes(
                  #"{}/{}.root".format(hist_path, year),
                  "{}/qcd_{}.root".format(hist_path, year),
                  "$BIN/$PROCESS",
                  "$BIN/$PROCESS_$SYSTEMATIC"
                  )

            for proc in procs:
                for category in cats:
                    category_name = category[1]
                    rate = cb.cp().process([proc]).bin([category_name]).GetRate()

                    if "D" in category_name:
                        abcd_string = proc+"_"+category_name.replace("_D", "_A")+"_rate,"
                        abcd_string += proc+"_"+category_name.replace("_D", "_C")+"_rate,"
                        abcd_string += proc+"_"+category_name.replace("_D", "_B")+"_rate"

                        cb.cp().process([proc]).bin([category_name]).AddSyst(cb, proc+"_"+category_name+"_rate", "rateParam",
                            ch.SystMap("era")([year], ("@0*@1/@2", abcd_string)) 
                        )
                    else:
                        cb.cp().process([proc]).bin([category_name]).AddSyst(cb, proc+"_"+category_name+"_rate", "rateParam",
                            #ch.SystMap("era")([year], rate)
                            ch.SystMap("era")([year], 1)
                        )


            bbFactory = ch.BinByBinFactory()
            bbFactory.SetAddThreshold(0.1)
            #bbFactory.SetMergeThreshold(0.5)
            bbFactory.SetFixNorm(True)
            bbFactory.SetPattern("bb_$BIN_$PROCESS_bin_$#")
            #bbFactory.MergeBinErrors(cb.cp().backgrounds())
            bbFactory.AddBinByBin(cb.cp().backgrounds(), cb)

            cb.PrintAll()
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
    "e",
    "mu",
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
print(category_pairs)

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
    print(icounter)
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

submit_file.write(")")
submit_file.write("\n")
submit_file.write("echo ${JOBS[$SGE_TASK_ID-1]}")
submit_file.write("\n")
submit_file.write("${JOBS[$SGE_TASK_ID-1]}")
submit_file.close()
