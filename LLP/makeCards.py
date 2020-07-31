import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json

def make_datacard(cats, signal_name, output_path):
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

        systematics = ["jesTotal", "jer", "pu", "trigger", "tight_muon_iso", "tight_muon_id"]

        for syst in systematics:
            cb.cp().AddSyst(cb, syst, "shape", ch.SystMap()(1.0))

        #cb.cp().process(['qcd']).AddSyst(cb, "bkg_$ERA", "lnN", ch.SystMap("era")(["2016"], 1.1))

        cb.cp().signals().ExtractShapes(
              "CombineHarvester/LLP/hists/{}_{}.root".format(signal_name, year),
              "$BIN/$PROCESS_{}".format(year),
              "$BIN/$PROCESS_{}_$SYSTEMATIC".format(year)
              )

        cb.cp().backgrounds().ExtractShapes(
              "CombineHarvester/LLP/hists/hist_{}.root".format(year),
              "$BIN/$PROCESS_{}".format(year),
              "$BIN/$PROCESS_{}_$SYSTEMATIC".format(year)
              )

        bbFactory = ch.BinByBinFactory()
        bbFactory.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(True)
        bbFactory.MergeBinErrors(cb.cp().backgrounds())
        bbFactory.AddBinByBin(cb.cp().backgrounds(), cb)

        cb.PrintAll()
        f = ROOT.TFile.Open(os.path.join(output_path,year+"_out.root"), "RECREATE")

        cb.cp().WriteDatacard(
            os.path.join(output_path,year+"_out.txt"),
            f
        )

        f.Close()

cats = [
    (0, "merged"),
]


i = 0
value_map = {}

hist_path = "CombineHarvester/LLP/hists/"
for proc in os.listdir(hist_path):
    if "HNL" not in proc:
        continue
    proc = proc.replace("_2016.root", "")
    print(proc)
    short_name=proc
    value_map[i] = short_name
    make_datacard(cats, short_name, os.path.join('CombineHarvester/LLP/cards', short_name))
    for year in ["2016"]:
        os.system("combine -M AsymptoticLimits -t -1 --cminPreScan --cminPreFit 1 \
              --rAbsAcc 0.000001 --run expected --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 \
              -d %s -n HNL --mass %s%i" %
              (os.path.join('CombineHarvester/LLP/cards', short_name, year+'_out.txt'), year, i))
    i += 1

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
