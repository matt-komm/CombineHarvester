import ROOT
import math
import os
import yaml
import json

# path to processed nanoAOD ntuples
ntuple_path = "/vols/cms/vc1117/LLP/nanoAOD_friends/HNL/25Mar20/"
lumi = {"2016": 35.88, "2017": 41.53, "2018": 58.83}

def find_xsec(path, xsecs):
    for key, val in xsecs.items():
        if key in path:     
            return val
    return 1


with open("/vols/build/cms/LLP/xsecs.yaml") as yaml_file:
    xsecs = yaml.load(yaml_file, Loader=yaml.FullLoader)


# This class prepares a given sample by scaling to int. luminosity
class Sample:
    def __init__(self, name, paths, isMC=True, year="2016"):
        self.paths = paths
        self.name = name
        self.file_list = ROOT.std.vector('string')()
        self.sum_weight = 0
        self.isMC = isMC
        for path in self.paths:
            for f in os.listdir(os.path.join(ntuple_path, path)):
                self.file_list.push_back(os.path.join(ntuple_path, path, f))
            if self.isMC:
                self.sum_weight += yields[path]["weighted"]
        self.rdf = ROOT.RDataFrame("Friends", self.file_list)
        if self.isMC:
            xsec = find_xsec(path, xsecs)
            # print(path, xsecs)
            self.rdf = self.rdf.Define("weightLumi", "IsoMuTrigger_weight_trigger_nominal*MET_filter*tightMuon_weight_iso_nominal*tightMuon_weight_id_nominal*looseMuons_weight_id_nominal*puweight*genweight*%s*1000.0*%s/%s" %(lumi[year], xsec, self.sum_weight))
        else:
            self.rdf = self.rdf.Define("weightLumi", "1")

        self.hists = []
        print("RDF "+name+ " has entries: "+str(self.rdf.Count().GetValue()))

# A process is a combination of several "Samples" which are all added up internally
class Process:
    def __init__(self, name):
        self.name = name
        self.rdfs = []
        self.hists = []

    def add(self, *args):
        for arg in args:
            self.rdfs.append(arg.rdf)

    def Histo1D(self, category, varexp, weight):
        for i, rdf in enumerate(self.rdfs):
            _rdf = rdf.Define(category, varexp)
            if i == 0:
                hist = _rdf.Histo1D((category, category, 2, 0, 2), category)
            else:
                tmp_hist = _rdf.Histo1D((category, category, 2, 0, 2), category)
                hist.Add(tmp_hist.GetValue())

        hist.SetName(self.name)
        hist.SetTitle(self.name)
        self.hists.append(hist)
        return self.hists[-1]

# for year in ["2018", "2017", "2016"]:
for year in ["2016"]:
    # Read in event yields and cross-sections for normalisation
    with open("/home/hep/vc1117/LLP/selection/eventyields"+year+".json") as json_file:
        yields = json.load(json_file)

    if year == "2016":
        qcd_15to20 = Sample("qcd_15to20", ["QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year) 
        qcd_20to30 = Sample("qcd_20to30", ["QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_30to50 = Sample("qcd_30to50", ["QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_50to80 = Sample("qcd_50to80", ["QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_80to120 = Sample("qcd_80to120", ["QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_120to170 = Sample("qcd_120to170", ["QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_170to300 = Sample("qcd_170to300", ["QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia-"+year], year=year)
        qcd_300to470 = Sample("qcd_300to470", ["QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_470to600 = Sample("qcd_470to600", ["QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_600to800 = Sample("qcd_600to800", ["QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year])
        qcd_800to1000 = Sample("qcd_800to1000", ["QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        qcd_1000toInf = Sample("qcd_1000toInf", ["QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8-"+year], year=year)
        ttsemilep = Sample("ttsemilep", ["TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8-"+year], year=year)
        ttdilep = Sample("ttdilep", ["TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8-"+year], year=year)

    else:
        qcd_15to20 = Sample("qcd_15to20", ["QCD_Pt-15to20_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year) 
        qcd_20to30 = Sample("qcd_20to30", ["QCD_Pt-20to30_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_30to50 = Sample("qcd_30to50", ["QCD_Pt-30to50_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_50to80 = Sample("qcd_50to80", ["QCD_Pt-50to80_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_80to120 = Sample("qcd_80to120", ["QCD_Pt-80to120_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_120to170 = Sample("qcd_120to170", ["QCD_Pt-120to170_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_170to300 = Sample("qcd_170to300", ["QCD_Pt-170to300_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_300to470 = Sample("qcd_300to470", ["QCD_Pt-300to470_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_470to600 = Sample("qcd_470to600", ["QCD_Pt-470to600_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_600to800 = Sample("qcd_600to800", ["QCD_Pt-600to800_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year])
        qcd_800to1000 = Sample("qcd_800to1000", ["QCD_Pt-800to1000_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)
        qcd_1000toInf = Sample("qcd_1000toInf", ["QCD_Pt-1000toInf_MuEnrichedPt5_TuneCP5_13TeV_pythia8-"+year], year=year)

        if year == "2017":
            ttsemilep = Sample("ttsemilep", ["TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_ext1-"+year], year=year)
            ttdilep = Sample("ttdilep", ["TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8-"+year], year=year)

        else:
            ttsemilep = Sample("ttsemilep", ["TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8-"+year], year=year)
            ttdilep = Sample("ttdilep", ["TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8-"+year], year=year)
           
    if year == "2016":
        #runb = Sample("RunBv2", ["SingleMuon_Run2016B_ver2"], isMC=False)
        #rune = Sample("RunE", ["SingleMuon_Run2016E"], isMC=False)
        #runf = Sample("RunF", ["SingleMuon_Run2016F"], isMC=False)
        #rung = Sample("RunG", ["SingleMuon_Run2016G"], isMC=False)
        #runh = Sample("RunH", ["SingleMuon_Run2016H"], isMC=False)
        w0jets = Sample("w0jets", ["WToLNu_0J_13TeV-amcatnloFXFX-pythia8-2016"], year=year)
        w1jets = Sample("w1jets", ["WToLNu_1J_13TeV-amcatnloFXFX-pythia8-2016"], year=year)
        w2jets = Sample("w2jets", ["WToLNu_2J_13TeV-amcatnloFXFX-pythia8-ext4-2016"], year=year)
        dy10to50 = Sample("dy10to50",  ["DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8-2016"], year=year)
        dy50 = Sample("dy50",  ["DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8-ext2-2016"], year=year)

    elif year == "2017":
        #runb = Sample("RunB", ["SingleMuon_Run2017B"], isMC=False)
        #rune = Sample("RunE", ["SingleMuon_Run2017E"], isMC=False)
        #runf = Sample("RunF", ["SingleMuon_Run2017F"], isMC=False)
        w0jets = Sample("w0jets", ["WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2017"], year=year)
        w1jets = Sample("w1jets", ["WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8-ext1-2017"], year=year)
        w2jets = Sample("w2jets", ["WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2017"], year=year)
        dy0jets = Sample("dy0jets", ["DYJetsToLL_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2017"], year=year)
        dy1jets = Sample("dy1jets", ["DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2017"], year=year)
        dy2jets = Sample("dy2jets", ["DYJetsToLL_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2017"], year=year)

    elif year == "2018":
        #runa = Sample("RunA", ["SingleMuon_Run2018A"], isMC=False)
        #runb = Sample("RunB", ["SingleMuon_Run2017B"], isMC=False)
        w0jets = Sample("w0jets", ["WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2018"], year=year)
        w1jets = Sample("w1jets", ["WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2018"], year=year)
        w2jets = Sample("w2jets", ["WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2018"], year=year)     
        dy0jets = Sample("dy0jets", ["DYJetsToLL_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2018"], year=year)
        dy1jets = Sample("dy1jets", ["DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2018"], year=year)
        dy2jets = Sample("dy2jets", ["DYJetsToLL_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8-2018"], year=year)

    '''
    runc = Sample("RunC", ["SingleMuon_Run"+year+"C"], isMC=False)
    rund = Sample("RunD", ["SingleMuon_Run"+year+"D"], isMC=False)
    data = Process("data", "data", "#000000")
    if year == "2016":
        data.add(runb, runc, rund, rune, runf, rung, runh)
    elif year == "2017":
        data.add(runb, runc, rund, rune, runf)
    elif year == "2018":
        data.add(runa, runb, runc, rund)
    #processes = [wjets, dyjets, tt, qcd, data]
    '''

    wjets = Process("wjets")
    wjets.add(w0jets, w1jets, w2jets)
    dyjets = Process("dyjets")
    if year == "2016":
        dyjets.add(dy10to50, dy50)
    else:
        dyjets.add(dy0jets, dy1jets, dy2jets)

    tt = Process("ttbar")
    tt.add(ttsemilep, ttdilep)
    qcd = Process("qcd")
    qcd.add(qcd_15to20, qcd_20to30, qcd_30to50, qcd_50to80, qcd_80to120, qcd_120to170, qcd_170to300, qcd_300to470, qcd_470to600, qcd_600to800, qcd_800to1000, qcd_1000toInf)

    processes = [wjets, dyjets, tt, qcd]


    for proc in os.listdir(ntuple_path):
        if "HeavyNeutrino" not in proc:
            continue
        short_name = proc.replace('HeavyNeutrino_lljj_', '').replace('_mu_Dirac_Moriond17_aug2018_miniAODv3-2016', '')
        sample = Sample(short_name, [proc])
        processes.extend([Process(short_name)])
        processes[-1].add(sample)


    signal_region_cut = "(weightLumi)*(ntightMuon == 1)*(nlepJet == 1)*(MET_pt < 100)*(nselectedJets<6)*(EventObservables_ht<200)*(dimuon_mass >30)*(dimuon_mass<80)" 
    tagger_cuts = {
        "merged_0": "lepJet_llpdnnx_0_isLLP_QMU_QQMU>0.999",
        "merged_1": "lepJet_llpdnnx_1_isLLP_QMU_QQMU>0.999",
        "merged_2": "lepJet_llpdnnx_2_isLLP_QMU_QQMU>0.999",
    }
    root_file = ROOT.TFile.Open("hists/merged.root", "RECREATE")
    for category, varexp in  tagger_cuts.items():
        print (category, varexp)
        root_file.cd()
        root_file.mkdir(category)
        root_file.cd(category)
        for process in processes:
            hist = process.Histo1D(category, varexp, "1")
            hist.SetDirectory(root_file)
            hist.Write()
    root_file.Close()
