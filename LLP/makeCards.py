import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import json
import argparse
import math
import subprocess
from multiprocessing import Pool

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

years = ["2016", "2017", "2018"]
couplings = [2, 7, 12, 47, 52]
#couplings = [12]
#couplings = range(2, 68)

def make_sge_script(procs):
    submit_file = open("runCombine.sh","w")
    submit_file.write('''#!/bin/bash
#$ -cwd
#$ -q hep.q
#$ -l h_rt=00:30:00
#$ -e log/log.$TASK_ID.err
#$ -o log/log.$TASK_ID.out
#$ -t 1-'''+str(4*n_job)+'''
hostname
date
source ~/.cms_setup.sh
eval `scramv1 runtime -sh`
''')

    submit_file.write("JOBS=(\n")

    for proc in procs:
        for coupling in couplings:
            for year in years:
                path = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}'.format(year, coupling, proc))
                submit_file.write(" \"")
                submit_file.write('''combineTool.py -M AsymptoticLimits --run expected --cminPreScan --cminPreFit 1 --rAbsAcc 0.000001 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 -d %s/out.txt --there -n HNL --mass %i''' % (path, coupling))
                #ssubmit_file.write('''combine -M FitDiagnostics --saveShapes --saveWithUncertainties -t -1 --expectSignal=1  -d %s/out.txt ''' % (path))
                submit_file.write("\"")
                submit_file.write("\n")
    
            path_2016 = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}/'.format(2016, coupling, proc))
            path_2017 = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}/'.format(2017, coupling, proc))
            path_2018 = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}/'.format(2018, coupling, proc))
            path_combined = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}/'.format("combined", coupling, proc))

            if not os.path.exists(path_combined):
                os.makedirs(path_combined)

            submit_file.write(" \"")
            submit_file.write("combineCards.py "+ path_2016+"out.txt " + path_2017 + "out.txt " + path_2018+"out.txt >> " +path_combined+"out.txt ")
            submit_file.write('''&& combineTool.py -M AsymptoticLimits --run expected --cminPreScan --cminPreFit 1 --rAbsAcc 0.000001 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 -d %sout.txt --there -n HNL --mass %i''' % (path_combined, coupling))
            submit_file.write("\"")
            submit_file.write("\n")


    submit_file.write(")")
    submit_file.write("\n")
    submit_file.write("echo ${JOBS[$SGE_TASK_ID-1]}")
    submit_file.write("\n")
    submit_file.write('''eval "${JOBS[$SGE_TASK_ID-1]}"''')
    submit_file.close()

def worker(proc):
    print("Started", str(hnl_sample_list.index(proc))+"/"+str(n_job/len(couplings)))
    for year in years:
        for coupling in couplings:
            path = os.path.join('CombineHarvester/LLP/cards/{}/coupling_{}/{}'.format(year, coupling, proc))
            make_datacard(category_pairs, category_pairs_signal, proc, path, coupling=coupling, year=year)

    print("Finished", str(hnl_sample_list.index(proc))+"/"+str(n_job/len(couplings)))



# make a datacard for a single HNL mass/coupling scenario
def make_datacard(cats, cats_signal, signal_name, output_path, coupling=12, year="2016"):
    cb = ch.CombineHarvester()
    bkgs_mc = ["ttbar"]
    bkgs_abcd = ["wjets", "dyjets", "qcd", "vgamma"]
    signal = ["HNL"]

    cb.AddProcesses(era=[year], procs=bkgs_mc, bin=cats, signal=False)
    cb.AddProcesses(era=[year], procs=signal, bin=cats_signal, signal=True) # for now no signal outside region D

    if os.path.exists(output_path):
        print("Overwriting path!")
    else:
        os.makedirs(output_path)

    systematics_correlated = ["jesTotal", "jer", "trigger", "tight_muon_iso", "tight_muon_id", "tight_electron_id", "tight_electron_reco", "loose_electron_reco"] #pu
    lumi_unc = {"2016": 1.025, "2017": 1.023, "2018": 1.025}
    for syst in systematics_correlated:
        cb.cp().AddSyst(cb, syst, "shape", ch.SystMap()(1.0))

    #for syst in systematics_uncorrelated:
        #cb.cp().AddSyst(cb, syst+"_$ERA", "shape", ch.SystMap("era")([year], 1.0))

    cb.cp().AddSyst(cb, "lumi_$ERA", "lnN", ch.SystMap("era")([year], lumi_unc[year]))

    cb.cp().signals().ExtractShapes(
            "{}/{}_{}.root".format(hist_path, signal_name, year),
            "$BIN/$PROCESS_coupling_{}".format(coupling),
            "$BIN/$PROCESS_coupling_{}_$SYSTEMATIC".format(coupling)
            )

    # FilterSysts(lambda sys: year not in sys.name())
    # .syst_name("*"+year).
    cb.cp().backgrounds().ExtractShapes(
            "{}/{}.root".format(hist_path, year),
            "$BIN/$PROCESS",
            "$BIN/$PROCESS_$SYSTEMATIC"
            )

    bbFactory = ch.BinByBinFactory()
    bbFactory.SetAddThreshold(0.1)
    bbFactory.SetMergeThreshold(0.5)
    bbFactory.SetFixNorm(True)
    bbFactory.SetPattern("bb_$ERA_$BIN_$PROCESS_bin_$#")
    bbFactory.AddBinByBin(cb.cp().process(bkgs_mc), cb)
            
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
        obs.set_shape(obs_sum_hist, True)
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
                syst_name = "rate_bkg_{}_bin{}_{}".format(name, ibin+1, year)

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
                    syst_name_A = syst_name.replace("_D", "_A")
                    syst_name_B = syst_name.replace("_D", "_B")
                    syst_name_C = syst_name.replace("_D", "_C")

                    cb.cp().process([process_name]).bin([name]).AddSyst(cb, syst_name, "rateParam",
                        ch.SystMap("era")([year],(
                        #"TMath::Max(@0,0.001)*TMath::Range(0,100.,TMath::Max(@1,0.000001)/TMath::Max(@2,0.000001))",
                        "@0*@1/@2",
                        syst_name_A+","+syst_name_C+","+syst_name_B
                    ))
                    )       
                else:
                    cb.cp().process([process_name]).bin([name]).AddSyst(cb, syst_name, "rateParam", ch.SystMap("era")([year], 1.))
                    param = cb.GetParameter(syst_name)

                    # Sum up all bkgs in mc to set initial param value
                    for i, bkg in enumerate(bkgs_abcd):
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
                    param.set_val(content) #content
                    param.set_range(0.1, 10*content)
                    #cb.cp().process([process_name]).AddSyst(cb, "rate_unc", "lnN", ch.SystMap("era")([year], 1.2))


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

hnl_sample_list = []
for proc in os.listdir(hist_path):
    if "HNL" not in proc:
        continue
    #if "HNL_majorana_all_ctau1p0e00_massHNL10p0_Vall1p177e-03" not in proc:
        #continue
    if "_2016" in proc:
        hnl_sample_list.append(proc.replace("_2016.root", ""))
        for coupling in couplings:
            n_job+=1

make_sge_script(hnl_sample_list)
    
#pool = Pool(16)
#pool.map(worker, hnl_sample_list)
