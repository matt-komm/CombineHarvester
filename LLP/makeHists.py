import ROOT
import math
import os
import yaml
import json
import random
import argparse

# make histograms per year, process
parser = argparse.ArgumentParser()
parser.add_argument("--year", dest='year', type=str, default="2016")
parser.add_argument("--proc", dest='proc', type=str, default="qcd")
parser.add_argument("--category", dest='category', type=str, default="mumu_OS")
parser.add_argument("--ntuple_path", dest="ntuple_path", default="/vols/cms/vc1117/LLP/nanoAOD_friends/HNL/21Sep20")
args = parser.parse_args()
year = args.year
proc = args.proc
ntuple_path = args.ntuple_path
# path to processed nanoAOD ntuples
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

#####################################
### Various configurations go here

# Systematic uncertainties
systDict = {}
systDict["IsoMuTrigger_weight_trigger"] = "trigger"
systDict["tightMuon_weight_iso"] = "tight_muon_iso"
systDict["tightMuon_weight_id"] = "tight_muon_id"
systDict["tightElectron_weight_id"] = "tight_electron_id"
systDict["puweight"] = "pu"

# so far optimised only for dilepton
def signal_region_cut(syst="nominal"):
    return "(EventObservables_{}_met<100.)*(nselectedJets_{}<6)".format(syst, syst)

def total_cut(category="dilepton", syst="nominal"):
    if category=="dilepton":
        return "(category_{}_taggerBestOutputValue[0]>0.7)*(bdt_score_{}>0.7)".format(syst, syst)
    elif category=="singlelepton":
        return "(category_{}_taggerBestOutputValue[0]>0.7)".format(syst)


macroCategory_dict = {}
macroCategory_dict["mumu_OS"] = "(Leptons_muonmuon>0)*(dilepton_charge<0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["mumu_SS"] = "(Leptons_muonmuon>0)*(dilepton_charge>0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["ee_OS"] = "(Leptons_electronelectron>0)*(dilepton_charge<0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["ee_SS"] = "(Leptons_electronelectron>0)*(dilepton_charge>0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["mue_OS"] = "(Leptons_muonelectron)*(dilepton_charge<0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["mue_SS"] = "(Leptons_muonelectron)*(dilepton_charge>0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["emu_OS"] = "(Leptons_electronmuon)*(dilepton_charge<0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["emu_SS"] = "(Leptons_electronmuon)*(dilepton_charge>0)*(dilepton_mass>30.)*(dilepton_mass<80.)"
macroCategory_dict["mu"] = "(Leptons_muonjets>0)"
macroCategory_dict["e"] = "(Leptons_electronjets>0)"

macroCategory = macroCategory_dict[args.category]

'''
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
'''


diLeptonCategory_dict = {}
diLeptonCategory_dict[-1] = "unsel"
diLeptonCategory_dict[1] = "q"
diLeptonCategory_dict[2] = "ql"
diLeptonCategory_dict[3] = "q+q"
diLeptonCategory_dict[4] = "ql+q"

singleLeptonCategory_dict = {}
singleLeptonCategory_dict[-1] = "unsel"
singleLeptonCategory_dict[5] = "q"
singleLeptonCategory_dict[6] = "q+q"

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
        #self.rdf = self.rdf.Filter("EventObservables_nominal_met < 100.")

        if self.isMC:
            if "HNL" in name:
                # 1 pb cross- section
                self.rdf = self.rdf.Define("weightLumi", "genweight*%s*1000.0" % (lumi[year]))
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
        print("RDF "+name+ " has entries: "+str(self.rdf.Count().GetValue()), flush=True)

# A process is a combination of several "Samples" which are all added up internally
class Process:
    def __init__(self, name):
        self.name = name
        self.rdfs = []
        self.hists = []

    def add(self, *args):
        for arg in args:
            self.rdfs.append(arg.rdf)

    def Histo1D(self, args, category, varexp, weight):
        for i, rdf in enumerate(self.rdfs):
            rdf = rdf.Define(category, varexp)
            weight_var = "weight_{}".format(random.randrange(1e6))
            rdf = rdf.Define(weight_var, weight)
            if i == 0:
                hist = rdf.Histo1D(args, category, weight_var)
                hist.Sumw2()
            else:
                tmp_hist = rdf.Histo1D(args, category, weight_var)
                tmp_hist.Sumw2()
                hist.Add(tmp_hist.GetValue())

        hist.SetName(self.name)
        hist.SetTitle(self.name)

        self.hists.append(hist)
        return self.hists[-1]


# Read in event yields and cross-sections for normalisation
with open("/vols/build/cms/LLP/yields_200720/{}/eventyields.json".format(year)) as json_file:
    yields = json.load(json_file)

with open("/vols/build/cms/LLP/yields_200720/{}/eventyieldsHNL.json".format(year)) as json_file:
    yieldsHNL = json.load(json_file)

if "HNL" in proc:
    yieldHNL = yieldsHNL["{}-{}".format(proc, year)]
    print(yieldHNL, flush=True)



# select only the relevant year

# slightly different syntax for hnl and SM/data
if "HNL" in proc:
    process = Process("hnl")
    process.add(Sample(proc, ["{}-{}".format(proc, year)], year=year))
else:
    samples = sample[int(year)]
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

category_variable_nominal = "category_nominal_allCategories"
root_file = ROOT.TFile.Open("hists/{}_{}_{}.root".format(proc, args.category, year), "RECREATE")

macroCategory_name = args.category
category_weight = macroCategory_dict[args.category]

print("The category name and weight are:", macroCategory_name, category_weight, flush=True)
root_file.cd()
root_file.mkdir(macroCategory_name)
root_file.cd(macroCategory_name)
coupling = 1

while coupling < 67:
    # different scenarios
    if "hnl" in process.name:
        coupling += 1
        print("coupling: {}/ 68".format(coupling))
        coupling_var = "(LHEWeights_coupling_{}/{})".format(coupling, yieldHNL["LHEWeights_coupling_{}".format(coupling)])
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
        varexp = category_weight.replace("nominal", systName)
        weight = "{}*{}".format(weight, varexp)
        category_variable = category_variable_nominal.replace("nominal", systName)

        if macroCategory_name in ["e", "mu"]:
            category_dict = singleLeptonCategory_dict
            category_variable += "*"+total_cut(category="singlelepton", syst=systName)
        else:
            category_dict = diLeptonCategory_dict
            category_variable += "*"+total_cut(category="dilepton", syst=systName)

        #print(category_variable, weight)

        # read in hist from nanoAOD friends
        hist_nano = process.Histo1D((category_variable, category_variable, 12, -2, 10), macroCategory_name, category_variable, weight)
        hist_nano = hist_nano.Clone()

        index_new = 0
        hist_limits = ROOT.TH1D("hist", "hist", len(category_dict), -0.5, len(category_dict)-0.5)

        for index, category in category_dict.items():
            index_new += 1
            hist_content = hist_nano.GetBinContent(hist_nano.FindBin(index))
            hist_limits.SetBinContent(index_new, hist_content)
            hist_limits.GetXaxis().SetBinLabel(index_new, category)
            #print(category, index, hist_nano.FindBin(index), index_new, hist_content)

        removeNegEntries(hist_limits)
        hist_limits.SetTitle(name)
        hist_limits.SetName(name)
        hist_limits.SetDirectory(root_file)
        hist_limits.Write()


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

            varexp = category_weight.replace("nominal", systName)
            weight = "{}*{}".format(weight, varexp)

            if macroCategory_name in ["e", "mu"]:
                category_dict = singleLeptonCategory_dict
                category_variable = category_variable_nominal+"*"+total_cut(category="singlelepton")
            else:
                category_dict = diLeptonCategory_dict
                category_variable = category_variable_nominal+"*"+total_cut(category="dilepton")

            # read in hist from nanoAOD friends
            hist_nano = process.Histo1D((category_variable, category_variable, 12, -2, 10), macroCategory_name, category_variable, weight)
            hist_nano = hist_nano.Clone()

            index_new = 0

            hist_limits = ROOT.TH1D("hist", "hist", len(category_dict), -0.5, len(category_dict)-0.5)

            for index, category in category_dict.items():
                index_new += 1
                hist_content = hist_nano.GetBinContent(hist_nano.FindBin(index))
                hist_limits.SetBinContent(index_new, hist_content)
                hist_limits.GetXaxis().SetBinLabel(index_new, category)
                #print(category, index, hist_nano.FindBin(index), index_new, hist_content)

            removeNegEntries(hist_limits)
            hist_limits.SetTitle(name)
            hist_limits.SetName(name)
            hist_limits.SetDirectory(root_file)
            hist_limits.Write()

root_file.Close()
