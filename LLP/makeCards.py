import CombineHarvester.CombineTools.ch as ch
import ROOT
import os


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

    cb.cp().process(['qcd', 'ttbar', 'wjets', 'dyjets']).AddSyst(cb,"bkg_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.3))

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
    (0, "merged_0"),
    (1, "merged_1"),
    (2, "merged_2"),
]


for proc in os.listdir(ntuple_path):
    if "HeavyNeutrino" not in proc:
        continue
    short_name = proc.replace('HeavyNeutrino_lljj_', '').replace('_mu_Dirac_Moriond17_aug2018_miniAODv3-2016', '')
    print(short_name)

    make_datacard(cats, short_name, os.path.join('CombineHarvester/LLP/cards', short_name))
    os.system("combine -M AsymptoticLimits --rAbsAcc 0.0000001 --saveToys -t -1 -d %s" % os.path.join('CombineHarvester/LLP/cards', short_name, 'out.txt'))
