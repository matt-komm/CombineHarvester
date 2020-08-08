import ROOT
import math
import os
import yaml
import json
import argparse

# make histograms per year, process
parser = argparse.ArgumentParser()
parser.add_argument("--year", dest='year', type=str, default="2016")
parser.add_argument("--proc", dest='proc', type=str, default="qcd")
args = parser.parse_args()
year = args.year
proc = args.proc
# path to processed nanoAOD ntuples
ntuple_path = "/vols/cms/vc1117/LLP/nanoAOD_friends/HNL/03Aug20/"
lumi = {"2016": 35.92, "2017": 41.53, "2018": 59.74}

def find_xsec(path, xsecs):
    for key, val in xsecs.items():
        if key in path: 
            return val
    return 1

with open("/vols/build/cms/LLP/xsec.yaml") as yaml_file:
    xsecs = yaml.load(yaml_file, Loader=yaml.FullLoader)

with open("samples.yaml") as samples_file:
    samples_dict = yaml.load(samples_file, Loader=yaml.FullLoader)
    sample = samples_dict[proc]

if "HNL" in proc:
    with open("/vols/build/cms/LLP/gridpackLookupTable.json") as lookup_table_file:
        lookup_table = json.load(lookup_table_file)[proc]
    print(lookup_table)

#####################################
### Various configurations go here

# Systematic uncertainties
systDict = {}
systDict["IsoMuTrigger_weight_trigger"] = "trigger"
systDict["tightMuon_weight_iso"] = "tight_muon_iso"
systDict["tightMuon_weight_id"] = "tight_muon_id"
systDict["tightElectron_weight_id"] = "tight_electron_id"
systDict["puweight"] = "pu"

# defined by Haifa
# so far optimised only for dilepton
def signal_region_cut(syst="nominal"):
    #return "(EventObservables_{}_met)*(nselectedJets_{}<6)*(EventObservables_{}_ht<180.)*(EventObservables_{}_mT_met_lep<80.)".format(syst, syst, syst, syst, syst)
    return "(EventObservables_{}_met<100.)".format(syst)

#### to be optimised by Haifa! ###
def total_cut(flavour="mu", syst="nominal"):
    if flavour=="mu":
        return "(category_{}_LLP_QMU_jet_output>0.9||category_{}_LLP_Q_jet_output>0.8)*(bdt_score>0.8)".format(syst, syst)
    elif flavour=="el":
        return "(category_{}_LLP_QE_jet_output>0.9||category_{}_LLP_Q_jet_output>0.8)*(bdt_score>0.8)".format(syst, syst)
    elif flavour=="jet":
        return "(category_{}_LLP_Q_jet_output>0.8)||(category_{}_LLP_QTAU_jet_output>0.8)".format(syst, syst)

category_varexp = "(category_nominal_muonmuon>0)*({})*(dilepton_charge==-1)*(dilepton_mass>20.)*(dilepton_mass<80.)*1".format(total_cut(flavour="mu"))
category_varexp = "{}+(category_nominal_muonmuon>0)*({})*(dilepton_charge==1)*(dilepton_mass>20.)*(dilepton_mass<80.)*2".format(category_varexp, total_cut(flavour="mu"))
category_varexp = "{}+(category_nominal_muonelectron>0)*({})*(dilepton_charge==-1)*(dilepton_mass>20.)*(dilepton_mass<80.)*3".format(category_varexp, total_cut(flavour="el"))
category_varexp = "{}+(category_nominal_muonelectron>0)*({})*(dilepton_charge==1)*(dilepton_mass>20.)*(dilepton_mass<80.)*4".format(category_varexp, total_cut(flavour="el"))
category_varexp = "{}+(category_nominal_electronelectron>0)*({})*(dilepton_charge==-1)*(dilepton_mass>20.)*(dilepton_mass<80.)*5".format(category_varexp, total_cut(flavour="el"))
category_varexp = "{}+(category_nominal_electronelectron>0)*({})*(dilepton_charge==1)*(dilepton_mass>20.)*(dilepton_mass<80.)*6".format(category_varexp, total_cut(flavour="el"))
category_varexp = "{}+(category_nominal_electronmuon>0)*({})*(dilepton_charge==-1)*(dilepton_mass>20.)*(dilepton_mass<80.)*7".format(category_varexp, total_cut(flavour="mu"))
category_varexp = "{}+(category_nominal_electronmuon>0)*({})*(dilepton_charge==1)*(dilepton_mass>20.)*(dilepton_mass<80.)*8".format(category_varexp, total_cut(flavour="mu"))
category_varexp = "{}+(category_nominal_muonjets>0)*({})*9".format(category_varexp, total_cut(flavour="jet"))
category_varexp = "{}+(category_nominal_electronjets>0)*({})*10".format(category_varexp, total_cut(flavour="jet"))

bin_labels = [
    "#mu#mu_OS",
    "#mu#mu_SS",
    "#mue_OS",
    "#mue_SS",
    "ee_OS",
    "ee_SS",
    "e#mu_OS",
    "e#mu_SS",
    "#mujets",
    "ejets"
]

print(category_varexp)
#####################################

# This class prepares a given sample by scaling to int. luminosity
class Sample:
    def __init__(self, name, paths, isMC=True, year="2016"):
        self.name = name
        self.file_list = ROOT.std.vector('string')()
        self.sum_weight = 0
        self.isMC = isMC
        for path in paths:
            for f in os.listdir(os.path.join(ntuple_path, path)):
                self.file_list.push_back(os.path.join(ntuple_path, path, f))
            if self.isMC:
                self.sum_weight += yields[path]
        self.rdf = ROOT.RDataFrame("Friends", self.file_list)
        # so far only dilepton
        self.rdf = self.rdf.Filter("EventObservables_nominal_met < 100.")

        if self.isMC:
            if "HNL" in name:
                # 1 pb cross- section
                self.rdf = self.rdf.Define("weightLumi", "genweight*%s*1000.0/%s" % (lumi[year], self.sum_weight))
            else:
                xsec = find_xsec(path, xsecs)
                self.rdf = self.rdf.Define("weightLumi", "genweight*%s*1000.0*%s/%s" % (lumi[year], xsec, self.sum_weight))

            # the nominal weights, the variations are derived from this
            self.rdf = self.rdf.Define("weightNominal", "MET_filter*weightLumi*IsoMuTrigger_weight_trigger_nominal * \
                                        tightMuon_weight_iso_nominal * \
                                        tightMuon_weight_id_nominal* \
                                        tightElectron_weight_id_nominal* \
                                        puweight_nominal"
                                        )

            for systName, abrv in systDict.items():
                for variation in ["Up", "Down"]:
                    self.rdf = self.rdf.Define("weight_{}{}".format(abrv, variation), "weightNominal/{}*{}".format(systName+"_nominal", systName+"_"+variation.lower()))
        else:
            self.rdf = self.rdf.Define("weightNominal", "1")

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

    def Histo1D(self, args, varexp, weight):
        category = args[0]
        for i, rdf in enumerate(self.rdfs):
            rdf = rdf.Define(category, varexp)
            _rdf = rdf.Define("weight", weight)
            if i == 0:
                hist = _rdf.Histo1D(args, category, "weight")
                hist.Sumw2()
            else:
                tmp_hist = _rdf.Histo1D(args, category, "weight")
                tmp_hist.Sumw2()
                hist.Add(tmp_hist.GetValue())

        hist.SetName(self.name)
        hist.SetTitle(self.name)
        for i, label in enumerate(bin_labels):
            hist.GetXaxis().SetBinLabel(i+1, label)
        self.hists.append(hist)
        return self.hists[-1]


# Read in event yields and cross-sections for normalisation
with open("/vols/build/cms/LLP/yields_200720/{}/eventyields.json".format(year)) as json_file:
    yields = json.load(json_file)

# select only the relevant year
samples = sample[int(year)]

# slightly different syntax for hnl and SM/data
# needs some imrpvoement
if "HNL" in proc:
    process = Process("hnl")
    process.add(Sample(proc, samples, year=year))
else:
    process = Process(proc)
    for subsample_name, subsample in samples.items():
        process.add(Sample(subsample_name, subsample ,year=year))


def removeNegEntries(hist):
    alpha = 1. - 0.6827
    upErr = ROOT.Math.gamma_quantile_c(alpha/2,1,1)
    avgWeight = hist.Integral()/hist.GetEntries() if hist.GetEntries()>0 else -1
    #print "weight",avgWeight
    for ibin in range(hist.GetNbinsX()):
        c = hist.GetBinContent(ibin+1)
        if c<10**-4:
            hist.SetBinContent(ibin+1,10**-3)
            #note: in case of 0 entries the uncertainty is also small
            #(this is not the case with negative events)
            if hist.GetBinError(ibin+1)<10**-4 and avgWeight>0:
                #set uncertainties for empy bins
                #https://twiki.cern.ch/twiki/bin/viewauth/CMS/PoissonErrorBars
                hist.SetBinError(ibin+1,upErr*avgWeight)
            else:
                hist.SetBinError(ibin+1,10**-4)
        #print "bin%2i, %.1f+-%.1f (+-%.1f%%)"%(ibin,c,hist.GetBinError(ibin+1),100.*hist.GetBinError(ibin+1)/c if c>0 else -1)


# create root file with nominal value histogram and various systematic variations
# to be used with Combine Harvester
root_file = ROOT.TFile.Open("hists/{}_{}.root".format(proc, year), "RECREATE")
root_file.cd()
root_file.mkdir("category")
root_file.cd("category")
coupling = 0

while coupling < 67:
    # different scenarios
    if "hnl" in process.name:
        coupling += 1
        coupling_var = "LHEWeights_coupling_{}".format(coupling)
    else:
        coupling = 68

    # variations with changing shape
    for systName in ["nominal", "jesTotalUp", "jesTotalDown", "jerUp", "jerDown"]:
        if "hnl" in process.name:
            name = "{}_coupling_{}_{}".format(process.name, coupling, year)
        else:
            name = "{}_{}".format(process.name, year)
        if systName != "nominal":
            name += "_"+systName
        weight = "weightNominal"
        if "hnl" in process.name:
            weight += "*"+coupling_var

        # Systematic variation
        varexp = category_varexp.replace("nominal", systName)

        print(name, varexp, weight)
        hist = process.Histo1D((name, name, 10, 0.5, 10.5), varexp, weight)
        removeNegEntries(hist)
        hist.SetTitle(name)
        hist.SetName(name)
        hist.SetDirectory(root_file)
        hist.Write()

    # variations with changing weight
    for systName, abrv in systDict.items():
        for variation in ["Up", "Down"]:
            if "hnl" in process.name:
                name = "{}_coupling_{}_{}_{}{}".format(process.name, coupling, year, abrv, variation)
            else:
                name = "{}_{}_{}{}".format(process.name, year, abrv, variation)
            weight = "weight_{}{}".format(abrv, variation)
            if "hnl" in process.name:
                weight += "*"+coupling_var
            print(name, category_varexp, weight)
            hist = process.Histo1D((name, name, 10, 0.5, 10.5), category_varexp, weight)
            removeNegEntries(hist)
            hist.SetTitle(name)
            hist.SetName(name)
            hist.SetDirectory(root_file)
            hist.Write()
root_file.Close()
