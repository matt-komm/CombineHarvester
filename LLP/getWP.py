import uproot
import ROOT
import json
import os
import numpy as np
import yaml


ntuple_path = "/vols/cms/vc1117/LLP/nanoAOD_friends/HNL/25Mar20/"
lumi = {"2016": 35.88, "2017": 41.53, "2018": 58.83}

tagger_strings = ["lepJet_llpdnnx_-1_isLLP_QMU_QQMU",
                  "lepJet_llpdnnx_0_isLLP_QMU_QQMU",
                  "lepJet_llpdnnx_1_isLLP_QMU_QQMU",
                  "lepJet_llpdnnx_2_isLLP_QMU_QQMU",
                  "lepJet_llpdnnx_3_isLLP_QMU_QQMU",
                 ]
combined_tagger_values = {}
combined_weight_values = {}

with open("/vols/build/cms/LLP/xsec.yaml") as yaml_file:
    xsecs = yaml.load(yaml_file, Loader=yaml.FullLoader)


for tagger_string in tagger_strings:
   combined_tagger_values[tagger_string] = []
   combined_weight_values[tagger_string] = []



def find_xsec(path, xsecs):
    for key, val in xsecs.items():
        if key in path: 
            return val
    return 1

def selection(tree):
    sel = (tree.array("MET_pt") < 80.) & \
          (tree.array("nselectedJets") < 6) & \
          (tree.array("EventObservables_ht") < 180.) & \
          (tree.array("dimuon_mass") < 80.) & \
          (tree.array("dimuon_mass") > 20.) & \
          (tree.array("nlepJet") == 1)
    return sel

def weight(tree, xsec, exp_yield):
    weight = tree.array("IsoMuTrigger_weight_trigger_nominal") \
            * tree.array("MET_filter") \
            * tree.array("tightMuon_weight_iso_nominal") \
            * tree.array("tightMuon_weight_id_nominal") \
            * tree.array("looseMuons_weight_id_nominal") \
            * tree.array("puweight") \
            * tree.array("genweight") \
            * 1000.0*xsec/exp_yield
    return weight


def Sample(name, paths, year="2016"):
    print("Reading in ", name)
    tagger_values = {}
    for tagger_string in tagger_strings:
        tagger_values[tagger_string] = []
    file_path = os.path.join(ntuple_path, paths[0])
    xsec = find_xsec(paths[0], xsecs)
    exp_yield = yields[paths[0]]["weighted"]
    for file in os.listdir(file_path):
        tree = uproot.open(os.path.join(file_path, file))["Friends"]
        for tagger_string in tagger_strings:
            sr_selection = selection(tree)
            tagger_array = tree.array(tagger_string)
            weight_array = weight(tree, xsec, exp_yield)
            weight_array = weight_array[sr_selection!=0]
            tagger_array = tagger_array[sr_selection!=0].flatten()
            combined_tagger_values[tagger_string].extend(tagger_array)
            combined_weight_values[tagger_string].extend(weight_array)



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

    for key, array in combined_tagger_values.items():
        indices = np.argsort(array)
        sorted_array = np.array(array)[indices]
        sorted_weights = np.array(combined_weight_values[key])[indices]
        exp_count = 0
        for i in reversed(range(len(sorted_array))):
            exp_count += sorted_weights[i]
            if exp_count >= 10:
                print("(%s>%s)" % (key, sorted_array[i]))
                break
        
