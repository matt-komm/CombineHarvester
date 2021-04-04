import CombineHarvester.CombineTools.ch as ch
import ROOT
import os
import argparse
import math
from multiprocessing import Pool
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

YEARS = ["2016", "2017", "2018"]
COUPLINGS = [2, 7, 12, 47, 52, 67] 
COUPLINGS = range(2, 68)

PSEUDO_DATA = 0

def getHist(fileName, histName):
    rootFile = ROOT.TFile(fileName)
    hist = rootFile.Get(histName)

    try:
        hist = hist.Clone()
        hist.SetDirectory(0)
    except:
        print("Could not read hist from file"+histName+fileName)
        return -1
    else:
        rootFile.Close()
        return hist

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
        for COUPLING in COUPLINGS:
            for YEAR in YEARS:
                path = os.path.join('$PWD/cards/{}/coupling_{}/{}'.format(YEAR, COUPLING, proc))
                submit_file.write(" \"")
                submit_file.write('''combineTool.py -M AsymptoticLimits --run expected \
                    --cminPreScan --cminPreFit 1 --rAbsAcc 0.000001 --X-rtd MINIMIZER_analytic \
                    --X-rtd MINIMIZER_MaxCalls=99999999999 -d %s/out.txt --there -n HNL --mass\
                    %i''' % (path, COUPLING))
                #ssubmit_file.write('''combine -M FitDiagnostics --saveShapes --saveWithUncertainties -t -1 --expectSignal=1  -d %s/out.txt ''' % (path))
                submit_file.write("\"")
                submit_file.write("\n")
    
            path_2016 = os.path.expandvars(os.path.join('$PWD/cards/{}/coupling_{}/{}/'.format(2016, COUPLING, proc)))
            path_2017 = os.path.expandvars(os.path.join('$PWD/cards/{}/coupling_{}/{}/'.format(2017, COUPLING, proc)))
            path_2018 = os.path.expandvars(os.path.join('$PWD/cards/{}/coupling_{}/{}/'.format(2018, COUPLING, proc)))
            path_combined = os.path.join('cards/{}/coupling_{}/{}/'.format("combined", COUPLING, proc))

            if not os.path.exists(path_combined):
                os.makedirs(path_combined)

            submit_file.write(" \"")
            submit_file.write("combineCards.py "+ path_2016+"out.txt " + path_2017 + "out.txt " + path_2018+"out.txt >> " +path_combined+"out.txt ")
            submit_file.write('''&& combineTool.py -M AsymptoticLimits --run expected --cminPreScan --cminPreFit 1 --rAbsAcc 0.000001 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 -d %sout.txt --there -n HNL --mass %i''' % (path_combined, COUPLING))
            submit_file.write("\"")
            submit_file.write("\n")


    submit_file.write(")")
    submit_file.write("\n")
    submit_file.write("echo ${JOBS[$SGE_TASK_ID-1]}")
    submit_file.write("\n")
    submit_file.write('''eval "${JOBS[$SGE_TASK_ID-1]}"''')
    submit_file.close()

def worker(proc):
    print("Started", str(hnl_sample_list.index(proc))+"/"+str(n_job/len(COUPLINGS)))
    for YEAR in YEARS:
        for COUPLING in COUPLINGS:
            path = os.path.join('cards/{}/coupling_{}/{}'.format(YEAR, COUPLING, proc))
            make_datacard(category_pairs, category_pairs_signal, proc, path, coupling=COUPLING, year=YEAR)

    print("Finished", str(hnl_sample_list.index(proc))+"/"+str(n_job/len(COUPLINGS)))

# make a datacard for a single HNL mass/coupling scenario
def make_datacard(cats, cats_signal, signal_name, output_path, coupling=12, year="2016"):
    cb = ch.CombineHarvester()
    bkgs_mc = []
    bkgs_abcd = ["wjets", "dyjets", "qcd", "vgamma", "topbkg"]
    signal = ["HNL"]

    cb.AddProcesses(era=[year], procs=bkgs_mc, bin=cats, signal=False)
    cb.AddProcesses(era=[year], procs=signal, bin=cats_signal, signal=True) 
    # TODO: for now no signal outside region D!

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    systematics_correlated = ["pu", "unclEn", "jesTotal", "jer", "trigger", "tight_muon_iso", "tight_muon_id", "tight_electron_id", "tight_electron_reco", "loose_electron_reco"]
caq
    lumi_uncertainty = {"2016": 1.025, "2017": 1.023, "2018": 1.025}

    for syst in systematics_correlated:
        cb.cp().AddSyst(cb, syst, "shape", ch.SystMap()(1.0))

    cb.cp().AddSyst(cb, "lumi_$ERA", "lnN", ch.SystMap("era")([year], lumi_uncertainty[year]))

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

    '''
    bbFactory = ch.BinByBinFactory()
    bbFactory.SetAddThreshold(0.1)
    bbFactory.SetMergeThreshold(0.5)
    bbFactory.SetFixNorm(True)
    bbFactory.SetPattern("bb_$ERA_$BIN_$PROCESS_bin_$#")
    bbFactory.AddBinByBin(cb.cp().process(bkgs_mc), cb)
    shape_hist = getHist(
        os.path.join(hist_path, "{}.root".format(year)),
        "mumu_OS_prompt_D/wjets"
    )

    nbins = shape_hist.GetNbinsX()
    bin_min = 0.5
    bin_max = nbins+0.5 """
    '''
    
    for _, category_name in cats:
        obs = ch.Observation()
        # pseudo-data = sum of MC
        if PSEUDO_DATA:
            for i, bkg in enumerate(bkgs_mc+bkgs_abcd):
                bkg_obs_hist = getHist(
                    os.path.join(hist_path,"{}.root".format(year)),
                        "{}/{}".format(category_name, bkg)
                )
                if i == 0:
                    obs_sum_hist = bkg_obs_hist.Clone(category_name)
                else:
                    obs_sum_hist.Add(bkg_obs_hist)
        else: #data
            obs_sum_hist = getHist(
                os.path.join(hist_path,"{}.root".format(year)),
                    "{}/{}".format(category_name, "data")
            )

        obs_sum_hist.SetDirectory(0)
        # Blinding
        if "D" in category_name:
            obs_sum_hist.Scale(0.)
        obs.set_shape(obs_sum_hist, True)
        obs.set_bin(category_name)
        obs.set_era(year)
        cb.InsertObservation(obs)

    # ABCD method
    cb.AddExtArgValue('xi', 1.0)
    cb.GetParameter('xi').set_range(0.8, 1.2)

    for _, category_name in cats_signal:
        if "single" in category_name:
            nbins = 1 # one bin
        else:
            nbins = 2 # merged + resolved
        bin_min = 0.5
        bin_max = nbins+0.5 
        for region in ["A","B","C", "D"]:
            name = category_name.replace("_D", "_"+region)
            for ibin in range(nbins):
                # Dummy histogram per bin , scale by rate parameters
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
                        "@0*(@1/@2)*@3",
                        syst_name_A+","+syst_name_C+","+syst_name_B+",xi"
                    ))
                    )       
                else:
                    cb.cp().process([process_name]).bin([name]).AddSyst(cb, syst_name, "rateParam", ch.SystMap("era")([year], 1.))
                    param = cb.GetParameter(syst_name)

                    # Set ABCD rate parameter values from MC or data:
                    if PSEUDO_DATA:
                        for i, bkg in enumerate(bkgs_abcd):
                            bkg_hist = getHist(
                                os.path.join(hist_path,"{}.root".format(year)),
                                    "{}/{}".format(name, bkg)
                            )
                            if i == 0:
                                bkg_hist_sum = bkg_hist.Clone(name)
                            else:
                                bkg_hist_sum.Add(bkg_hist)
                    else:
                        bkg_hist_sum = getHist(
                            os.path.join(hist_path,"{}.root".format(year)),
                                "{}/{}".format(name, "data")
                        )

                    content = max(0.,bkg_hist_sum.GetBinContent(ibin+1))
                    err = max(0.,math.sqrt(bkg_hist_sum.GetBinContent(ibin+1)))
                    param.set_val(content)
                    param.set_range(max(0, content-10*err), content+10*err)


    #cb.PrintAll()
    f = ROOT.TFile.Open(os.path.join(output_path, "out.root"), "RECREATE")

    cb.cp().WriteDatacard(
        os.path.join(output_path, "out.txt"),
        f
    )

    f.Close()
    return True

parser = argparse.ArgumentParser()

parser.add_argument("--path", default="/vols/cms/vc1117/AN-19-207/classes/hists_merged")
args = parser.parse_args()
hist_path = args.path

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
    # "mu_single",
    # "e_single"
]

n_categories = len(categories)

category_pairs = []
category_pairs_signal = [] # So far signal only in region D (to save CPU time)

for index1, category_name in enumerate(categories):
    for index2, region in enumerate(["A", "B", "C", "D"]):
        index = index1*4 + index2 
        name = category_name+"_"+region
        pair=(index, name)
        if region == "D":
            category_pairs_signal.append(pair)
        category_pairs.append(pair)


# Count the number of jobs
hnl_sample_list = []
n_job = 0
for proc in os.listdir(hist_path):
    if "HNL" not in proc:
        continue
    if "_2016" in proc:
        hnl_sample_list.append(proc.replace("_2016.root", ""))
        for coupling in COUPLINGS:
            n_job += 1

# Make sge submission script
make_sge_script(hnl_sample_list)
    
# Make cards in parallel 
pool = Pool(16)
pool.map(worker, hnl_sample_list)
