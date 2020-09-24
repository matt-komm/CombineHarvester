import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json

years = ["2016"]
couplings = [2, 7, 12, 47, 52, 67]
couplings=range(2, 68)

# make a datacard for a single HNL mass/coupling scenario
def make_datacard(cats, signal_name, output_path, coupling=12):
    for year in years:
        cb = ch.CombineHarvester()
        procs = ["ttbar", "qcd", "wjets", "dyjets"]
        signal = ["hnl"]

        cb.AddProcesses(era=[year], procs=procs, bin=cats, signal=False)
        cb.AddProcesses(era=[year], procs=signal, bin=cats, signal=True)

        if os.path.exists(output_path):
            print("Overwriting path!")
        else:
            os.makedirs(output_path)

        systematics = ["jesTotal", "jer", "pu", "trigger", "tight_muon_iso", "tight_muon_id", "tight_electron_id"]

        for syst in systematics:
            cb.cp().AddSyst(cb, syst, "shape", ch.SystMap()(1.0))

        cb.cp().AddSyst(cb, "lumi_$ERA", "lnN", ch.SystMap("era")([year], 1.026))

        cb.cp().signals().ExtractShapes(
              "CombineHarvester/LLP/hists/{}_{}.root".format(signal_name, year),
              "$BIN/$PROCESS_coupling_{}_{}".format(coupling, year),
              "$BIN/$PROCESS_coupling_{}_{}_$SYSTEMATIC".format(coupling, year)
              )

        cb.cp().backgrounds().ExtractShapes(
              "CombineHarvester/LLP/hists/{}.root".format(year),
              "$BIN/$PROCESS_{}".format(year),
              "$BIN/$PROCESS_{}_$SYSTEMATIC".format(year)
              )

        '''
        bbFactory = ch.BinByBinFactory()
        bbFactory.SetAddThreshold(0.1)
        #bbFactory.SetMergeThreshold(0.5)
        bbFactory.SetFixNorm(True)
        bbFactory.SetPattern("bb_$BIN_$PROCESS_bin_$#")
        #bbFactory.MergeBinErrors(cb.cp().backgrounds())
        bbFactory.AddBinByBin(cb.cp().backgrounds(), cb)
        '''

        cb.PrintAll()
        f = ROOT.TFile.Open(os.path.join(output_path, "out.root"), "RECREATE")

        cb.cp().WriteDatacard(
            os.path.join(output_path, "out.txt"),
            f
        )

        f.Close()

# WIP -- expand into merged and resolved!
cats = [
    (0, "category"),
]

hist_path = "CombineHarvester/LLP/hists/"

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
#$ -l h_rt=00:30:00 
#$ -e log/log.$TASK_ID.err
#$ -o log/log.$TASK_ID.out
#$ -t 1-'''+str(n_job)+'''
hostname
date
source ~/.cms_setup.sh
cd /home/hep/vc1117/LLP/CMSSW_10_2_13/src
eval `scramv1 runtime -sh`
''')

submit_file.write("JOBS=(\n")
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
            make_datacard(cats, name, os.path.join(path), coupling=coupling)
            submit_file.write(" \"")
            submit_file.write('''combineTool.py -M AsymptoticLimits -t -1 --cminPreScan --cminPreFit 1 --rAbsAcc 0.000001 --run expected --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 -d %s/out.txt --there -n HNL --mass %i''' % (path, coupling))
            submit_file.write("\"")
            
submit_file.write(")")
submit_file.write("\n")
submit_file.write("echo ${JOBS[$SGE_TASK_ID]}")
submit_file.write("\n")
submit_file.write("${JOBS[$SGE_TASK_ID]}")
submit_file.close()
