import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json

# make a datacard for a single HNL mass/coupling scenario
def make_datacard(cats, signal_name, output_path, coupling=12):
    #for year in ["2016", "2017", "2018"]:
    for year in ["2016"]:
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
              "CombineHarvester/LLP/hists/hist_{}.root".format(year),
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
for proc in os.listdir(hist_path):
    if "HNL" not in proc:
        continue
    for year in ["2016"]:
        if year not in proc:
            continue
        for coupling in [2, 12, 67]:
            # parse name
            name = proc.replace("_{}.root".format(year), "")
            path = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}'.format(year, coupling, name))
            make_datacard(cats, name, os.path.join(path), coupling=coupling)
            os.system("(cd %s && combine -M AsymptoticLimits -t -1 --cminPreScan --cminPreFit 1 \
                  --rAbsAcc 0.000001 --run expected --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 \
                  -d out.txt -n HNL)" % (os.path.join(path)))
    break

# Needs to be rewritten!
'''
for year in ["2016"]:
#os.system("combineTool.py -M CollectLimits higgsCombineHNL.AsymptoticLimits.mH*.root")
    os.system("combineTool.py -M CollectLimits higgsCombineHNL.AsymptoticLimits.mH{}*.root".format(year))

    with open('limits.json') as f:
        combine_json = json.load(f)

    limit_json = {}
    for key, value in combine_json.iteritems():
        key = int(float(key.replace(year, "")))
        limit_json[value_map[key]] = value

    with open('limitDict{}.json'.format(year), 'w') as f:
        json.dump(limit_json, f)
'''