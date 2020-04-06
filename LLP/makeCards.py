import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json

ntuple_path = "/vols/cms/vc1117/LLP/nanoAOD_friends/HNL/25Mar20/"


def make_datacard(cats, signal_hist, output_path):
    cb = ch.CombineHarvester()

    cb.AddProcesses(era=["13TeV2016"], procs=["ttbar", "qcd", "wjets", "dyjets"], bin=cats, signal=False)
    cb.AddProcesses(era=["13TeV2016"], procs=[signal_hist], bin=cats, signal=True)

    print(signal_hist)

    cb.cp().ExtractShapes(
          "CombineHarvester/LLP/hists/merged.root",
          "$BIN/$PROCESS",
          ""
          )

    if os.path.exists(output_path):
        print "Overwriting path!"
    else:
        os.makedirs(output_path)

    cb.cp().process(['qcd']).AddSyst(cb,"bkg_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.1))

    bbFactory = ch.BinByBinFactory()
    bbFactory.SetAddThreshold(0.1)
    bbFactory.SetFixNorm(True)
    bbFactory.AddBinByBin(cb.cp().backgrounds(), cb)
    ch.SetStandardBinNames(cb)

    cb.PrintAll()
    file = ROOT.TFile.Open(os.path.join(output_path,"out.root"), "RECREATE")

    cb.cp().WriteDatacard(
        os.path.join(output_path,"out.txt"),
        file
    )

    file.Close()


cats = [
    (0, "merged"),
]

i = 0
value_map = {}
for proc in os.listdir(ntuple_path):
    if "HeavyNeutrino" not in proc:
        continue
    i += 1
    short_name = proc.replace('HeavyNeutrino_lljj_', '').replace('_mu_Dirac_Moriond17_aug2018_miniAODv3-2016', '')
    value_map[i] = short_name
    make_datacard(cats, short_name, os.path.join('CombineHarvester/LLP/cards', short_name))
    os.system("combine -M AsymptoticLimits -t -1 \
              --rAbsAcc 0.000001 --run expected --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 \
              -d %s -n HNL --mass %i" %
              (os.path.join('CombineHarvester/LLP/cards', short_name, 'out.txt'), i))

os.system("combineTool.py -M CollectLimits higgsCombineHNL.AsymptoticLimits.mH*.root")

with open('limits.json',) as f:
    combine_json = json.load(f)

limit_json = {}
for key, value in combine_json.iteritems():
    int_key = int(float(key))
    limit_json[value_map[int_key]] = value


with open('limitDict.json', 'w') as f:
    json.dump(limit_json, f)