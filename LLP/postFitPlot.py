import CombineHarvester.CombineTools.plotting as plot
import ROOT
import style
import os
from array import array

lumi = {"2016": 35.88, "2017": 41.53, "2018": 59.68}
fin = ROOT.TFile('CombineHarvester/LLP/cards/2016/coupling_7/HNL_majorana_all_ctau1p0e00_massHNL10p0_Vall1p177e-03/shapes.root')
categories = [
    "mumu_OS_displaced",
    "ee_OS_displaced",
    "mue_OS_displaced",
    "emu_OS_displaced",
    "mumu_OS_prompt",
    "ee_OS_prompt",
    "mue_OS_prompt",
    "emu_OS_prompt",
    "mumu_SS_displaced",
    "ee_SS_displaced",
    "mue_SS_displaced",
    "emu_SS_displaced",
    "mumu_SS_prompt",
    "ee_SS_prompt",
    "mue_SS_prompt",
    "emu_SS_prompt",
    #"e",
    #"mu",
]

categories = [category+"_D" for category in categories]


def getHist(fileName, histName):
    rootFile = ROOT.TFile(fileName)
    hist = rootFile.Get(histName)
    hist = hist.Clone()
    hist.SetDirectory(0)
    rootFile.Close()
    return hist


def get_observed_expected_distributions(title, categories, hist_path="/home/hep/vc1117/LLP/histo/hists_merged"):
    print(title)
    n_categories = len(categories)

    hist_shape = getHist(
    os.path.join(hist_path, "{}.root".format(2016)),
    "mumu_OS_prompt_D/ttbar"
        )

    n_bins = hist_shape.GetNbinsX()
    n_bins_total = n_bins * n_categories

    master_hist_observed = ROOT.TH1F(title, title, n_bins_total, -0.5, n_bins_total-0.5)
    master_hist_expected = ROOT.TH1F(title, title, n_bins_total, -0.5, n_bins_total-0.5)

    for i, category_name in enumerate(categories):
        for k, bkg in enumerate(["wjets"]):
            bkg_obs_hist_A = getHist(
                os.path.join(hist_path,"{}.root".format(2016)),
                    "{}/{}".format(category_name.replace("_D", "_A"), bkg)
            )
            bkg_obs_hist_B = getHist(
                os.path.join(hist_path,"{}.root".format(2016)),
                    "{}/{}".format(category_name.replace("_D", "_B"), bkg)
            )
            bkg_obs_hist_C = getHist(
                os.path.join(hist_path,"{}.root".format(2016)),
                    "{}/{}".format(category_name.replace("_D", "_C"), bkg)
            )
            bkg_obs_hist_D = getHist(
                os.path.join(hist_path,"{}.root".format(2016)),
                    "{}/{}".format(category_name, bkg)
            )
            if k == 0:
                hA = bkg_obs_hist_A
                hB = bkg_obs_hist_B
                hC = bkg_obs_hist_C
                hD = bkg_obs_hist_D
            else:
                hA.Add(bkg_obs_hist_A)
                hB.Add(bkg_obs_hist_B)
                hC.Add(bkg_obs_hist_C)
                hD.Add(bkg_obs_hist_D)

        for j in range(hD.GetNbinsX()):
            bin_name = replace_name(category_name)
            h_expected = hA * hC
            h_expected.Divide(hB)
            bin_index = j*n_categories+i+1
            print(i, j, category_name, bin_index, hD.GetBinContent(j+1), hD.GetBinError(j+1))
            print(i, j, category_name, bin_index, h_expected.GetBinContent(j+1), h_expected.GetBinError(j+1))


            master_hist_observed.SetBinContent(bin_index, hD.GetBinContent(j+1))
            master_hist_observed.SetBinError(bin_index, hD.GetBinError(j+1))
            master_hist_observed.GetXaxis().SetBinLabel(bin_index, bin_name)
            master_hist_observed.GetXaxis().LabelsOption("v")

            master_hist_expected.SetBinContent(bin_index, h_expected.GetBinContent(j+1))
            master_hist_expected.SetBinError(bin_index, h_expected.GetBinError(j+1))
            master_hist_expected.GetXaxis().SetBinLabel(bin_index, bin_name)
            master_hist_expected.GetXaxis().LabelsOption("v")
    return master_hist_observed, master_hist_expected


def replace_name(name):
    out = ""
    if "mumu" in name:
        out += "#mu#mu"
    elif "ee" in name:
        out += "ee"
    elif "mue" in name:
        out += "e#mu"    
    elif "emu" in name:
        out += "#mue"
    return out

def expand_hist(name, title, hist_type="mc", fit_type="prefit", categories=categories):
    print(name, title)

    n_categories = len(categories)
    print(categories[0] + "_" + fit_type + "/ttbar")
    hist_shape = fin.Get(categories[0] + "_" + fit_type + "/ttbar")
    n_bins = hist_shape.GetNbinsX()

    n_bins_total = n_bins * n_categories
    print(n_bins_total)

    if hist_type == 'abcd':
        master_hist = ROOT.TH1F(title, title, n_bins_total, -0.5, n_bins_total-0.5)

        for i, category_name in enumerate(categories):
            h = fin.Get(category_name + "_" + fit_type + "/bkg_" + category_name + "_bin1")
            h2 = fin.Get(category_name + "_" + fit_type + "/bkg_" + category_name + "_bin2")
            h.Add(h2)
            for j in range(h.GetNbinsX()):
                if j == 0:
                    bin_name = replace_name(category_name)
                if j == 1:
                    bin_name = ""
                master_hist.GetXaxis().SetBinLabel(i*n_bins+j+1, bin_name)
                master_hist.GetXaxis().LabelsOption("v")

                print(i, j, category_name, i*n_bins+j, h.GetBinContent(j+1), h.GetBinError(j+1))
                master_hist.SetBinContent(i*n_bins+j+1, h.GetBinContent(j+1))
                master_hist.SetBinError(i*n_bins+j+1, h.GetBinError(j+1))
    
    else:
        master_hist = ROOT.TH1F(title, title, n_bins_total, -0.5, n_bins_total-0.5)

        for i, category_name in enumerate(categories):
            h = fin.Get(category_name + "_" + fit_type + "/" + name)
            for j in range(h.GetNbinsX()):
                bin_name = replace_name(category_name)

                print(i, j, category_name, i*n_bins+j, h.GetBinContent(j+1), h.GetBinError(j+1))

                master_hist.GetXaxis().SetBinLabel(i*n_bins+j+1, bin_name);
                master_hist.GetXaxis().LabelsOption("v")

                master_hist.SetBinContent(i*n_bins+j+1, h.GetBinContent(j+1))
                master_hist.SetBinError(i*n_bins+j+1, h.GetBinError(j+1))

    
    return master_hist

for fit_type in ["prefit"]:#, "postfit"]:

    ROOT.PyConfig.IgnoreCommandLineOptions = True
    ROOT.gROOT.SetBatch(ROOT.kTRUE)

    canvas = style.makeCanvas("cv", 1600, 800)
    #canvas.SetLeftMargin(0.09)
    canvas.SetRightMargin(0.15)
    canvas.SetBottomMargin(0)
    #canvas.SetLogy()

    pad1 = ROOT.TPad("pad1","pad1",0,0.35,1,1)
    pad2 = ROOT.TPad("pad2","pad2",0,0.03,1,0.35)
    pad1.SetBottomMargin(0.00001)
    pad1.SetRightMargin(0.15)
    pad1.SetBorderMode(0)
    pad1.SetLogy()

    pad2.SetTopMargin(0.00001)
    pad2.SetRightMargin(0.15)
    pad2.SetBottomMargin(0.3)
    pad2.SetBorderMode(0)
    pad1.Draw()
    pad2.Draw()
    pad1.cd()


    ttbar = expand_hist('ttbar', 'ttbar', fit_type=fit_type)
    #observed = expand_hist('data_obs', 'observed', hist_type='data', fit_type=fit_type)
    #expected = expand_hist('data', 'expected', hist_type='abcd', fit_type=fit_type)
    observed, expected = get_observed_expected_distributions(title='test', categories=categories)
    hnl = expand_hist('HNL', 'HNL', fit_type="prefit")

    hnl.SetFillStyle(0)
    hnl.SetLineColor(ROOT.kRed)
    hnl.SetLineWidth(3)

    #ef5350
    ttbar.SetFillColor(ROOT.kRed-7)
    ttbar.SetLineColor(ROOT.kRed-7)

    expected.SetFillColor(ROOT.kAzure+1)
    expected.SetLineColor(ROOT.kAzure+1)

    #expected.SetFillColor(ROOT.TColor.GetColor(colorscale("#1976d2", 1)))
    #expected.SetLineColor(ROOT.TColor.GetColor(colorscale("#1976d2", 0.8)))
    exp_err = expected.Clone()
    #exp_err.Add(ttbar)
    exp_err.SetFillColor(ROOT.kAzure+2)
    exp_err.SetFillStyle(3244)  # Set grey colour (12) and alpha (0.3)
    exp_err.SetMarkerSize(0)
    exp_err.SetMarkerColor(12)
    hs = ROOT.THStack("hs", "hs")

    #ttbar.Draw('SAME')
    #exp_err.SetFillColor(ROOT.kAzure+1)  # Set grey colour (12) and alpha (0.3)
    #hs.Add(ttbar)
    #hs.Add(expected)
    expected.Draw("HIST")

    expected.GetXaxis().SetTitle("Bin number")
    expected.GetYaxis().SetTitle("Number of events")
    expected.GetYaxis().SetTitleOffset(1)
    expected.GetXaxis().SetTitleOffset(10)
    expected.Draw("HIST")

    l_merged_resolved = ROOT.TLine(expected.GetNbinsX()/2-0.5, 0, expected.GetNbinsX()/2-0.5, expected.GetMaximum() * 3)
    l_prompt_displaced = ROOT.TLine(expected.GetNbinsX()/4-0.5, 0, expected.GetNbinsX()/4-0.5, expected.GetMaximum() * 3)
    l_prompt_displaced_2 = ROOT.TLine(expected.GetNbinsX()*3/4-0.5, 0, expected.GetNbinsX()*3/4-0.5, expected.GetMaximum() * 3)
    l_OS_SS = ROOT.TLine(expected.GetNbinsX()/8-0.5, 0, expected.GetNbinsX()/8-0.5, expected.GetMaximum() * 3)
    l_OS_SS_2 = ROOT.TLine(expected.GetNbinsX()*7/8-0.5, 0, expected.GetNbinsX()*7/8-0.5, expected.GetMaximum() * 3)
    l_OS_SS_3 = ROOT.TLine(expected.GetNbinsX()*3/8-0.5, 0, expected.GetNbinsX()*3/8-0.5, expected.GetMaximum() * 3)
    l_OS_SS_4 = ROOT.TLine(expected.GetNbinsX()*5/8-0.5, 0, expected.GetNbinsX()*5/8-0.5, expected.GetMaximum() * 3)
    l_merged_resolved.SetLineWidth(3)
    l_prompt_displaced.SetLineWidth(3)
    l_prompt_displaced_2.SetLineWidth(3)
    l_OS_SS.SetLineWidth(2)
    l_OS_SS_2.SetLineWidth(2)
    l_OS_SS_3.SetLineWidth(2)
    l_OS_SS_4.SetLineWidth(2)
    l_prompt_displaced.SetLineStyle(2)
    l_prompt_displaced_2.SetLineStyle(2)

    l_OS_SS.SetLineStyle(3)
    l_OS_SS_2.SetLineStyle(3)
    l_OS_SS_3.SetLineStyle(3)
    l_OS_SS_4.SetLineStyle(3)

    l_merged_resolved.Draw("")
    l_prompt_displaced.Draw("")
    l_prompt_displaced_2.Draw("")
    l_OS_SS.Draw("")
    l_OS_SS_2.Draw("")
    l_OS_SS_3.Draw("")
    l_OS_SS_4.Draw("")
    observed.Draw('PSAME')
    exp_err.Draw('E2SAME')

    text_resolved = ROOT.TText(2.5, expected.GetMaximum(), "resolved")
    text_merged = ROOT.TText(expected.GetNbinsX()/2+2, expected.GetMaximum(), "merged")

    text_OS = ROOT.TText(1, 0.4*expected.GetMaximum(), "OS")
    text_SS = ROOT.TText(expected.GetNbinsX()*1/4+1, 0.4*expected.GetMaximum(), "SS")
    text_OS_2 = ROOT.TText(expected.GetNbinsX()*2/4+1, 0.4*expected.GetMaximum(), "OS")
    text_SS_2 = ROOT.TText(expected.GetNbinsX()*3/4+1, 0.4*expected.GetMaximum(), "SS")

    text_prompt = ROOT.TText(expected.GetNbinsX()/8+2, 0.1*expected.GetMaximum(), "prompt")
    text_prompt_2 = ROOT.TText(expected.GetNbinsX()*3/8+2, 0.1*expected.GetMaximum(), "prompt")
    text_prompt_3 = ROOT.TText(expected.GetNbinsX()*5/8+2, 0.1*expected.GetMaximum(), "prompt")
    text_prompt_4 = ROOT.TText(expected.GetNbinsX()*7/8+2, 0.1*expected.GetMaximum(), "prompt")

    text_displaced = ROOT.TText(2.5, 0.1*expected.GetMaximum(), "displaced")
    text_displaced_2 = ROOT.TText(expected.GetNbinsX()*1/4+2.5, 0.1*expected.GetMaximum(), "displaced")
    text_displaced_3 = ROOT.TText(expected.GetNbinsX()*2/4+2.5, 0.1*expected.GetMaximum(), "displaced")
    text_displaced_4 = ROOT.TText(expected.GetNbinsX()*3/4+2.5, 0.1*expected.GetMaximum(), "displaced")

    text_resolved.SetTextAlign(31)
    text_merged.SetTextAlign(31)
    text_prompt.SetTextAlign(31)
    text_prompt_2.SetTextAlign(31)
    text_prompt_3.SetTextAlign(31)
    text_prompt_4.SetTextAlign(31)
    text_displaced.SetTextAlign(31)
    text_displaced_2.SetTextAlign(31)
    text_displaced_3.SetTextAlign(31)
    text_displaced_4.SetTextAlign(31)

    text_OS.SetTextAlign(31)
    text_OS_2.SetTextAlign(31)
    text_SS.SetTextAlign(31)
    text_SS_2.SetTextAlign(31)

    #text.SetTextFont(43)
    #text.SetTextSize(40)
    #text_resolved.SetTextAngle(45)
    text_merged.Draw("")
    text_resolved.Draw("")
    text_prompt.Draw("")
    text_prompt_2.Draw("")
    text_prompt_3.Draw("")
    text_prompt_4.Draw("")
    text_displaced.Draw("")
    text_displaced_2.Draw("")
    text_displaced_3.Draw("")
    text_displaced_4.Draw("") 
    text_OS.Draw("")
    text_OS_2.Draw("")
    text_SS.Draw("")
    text_SS_2.Draw("")

    hnl.Draw("HISTSAME")

    hs.SetMaximum(hs.GetMaximum() * 3)
    pad2.cd()

    #sum_hist = hs.GetStack().Last().Clone("sum")
    residuals = observed.Clone("res")
    residuals.Sumw2()
    residuals.Divide(expected)#(sum_hist)
    residuals.GetYaxis().SetTitle("data/MC")
    residuals.GetYaxis().SetTitleOffset(1)
    residuals.GetYaxis().SetNdivisions(505)
    residuals.GetYaxis().SetRangeUser(0, 10.1)
    residuals.Draw("P")

    lres = ROOT.TLine(-0.5, 1., expected.GetNbinsX()-0.5, 1.)
    lres.Draw("SAME")
    '''
    h = fin.Get(postfit_dir + '/' + category_name + '/' + name)

    for j in range(h.GetN()):
        x_lower_arr.append(float(h.GetErrorXlow(j)))
        x_higher_arr.append(float(h.GetErrorXhigh(j)))
        y_lower_arr.append(float(h.GetErrorYlow(j)))
        y_higher_arr.append(float(h.GetErrorYhigh(j)))
        h.GetPoint(j, x, y)
        print(i, j, category_name, i*n_bins+j, float(y))
        x_arr.append(i*n_bins+j)
        y_arr.append(float(y))
    x_arr = array('d', x_arr)
    y_arr = array('d', y_arr)
    x_lower_arr = array('d', x_lower_arr)
    x_higher_arr = array('d', x_higher_arr)
    y_lower_arr = array('d', y_lower_arr)
    y_higher_arr = array('d', y_higher_arr)
    master_hist = ROOT.TGraphAsymmErrors(n_bins_total, x_arr, y_arr, x_lower_arr, x_higher_arr, y_lower_arr, y_higher_arr)
    '''

    canvas.cd()

    legend = style.makeLegend (0.87, 0.6, 0.95, 0.8)
    legend.AddEntry(expected, 'predicted', 'F')
    #legend.AddEntry(ttbar, 'tt', "F")
    legend.AddEntry(observed, 'observed', "p")
    legend.AddEntry(hnl, 'signal', "l")
    legend.Draw("")

    style.makeCMSText(0.15, 0.97, additionalText="Simulation Preliminary", dx=0.043)
    style.makeLumiText(0.86, 0.97, year="2016", lumi=lumi["2016"])
    canvas.SaveAs('plot_{}.pdf'.format(fit_type))
    canvas.SaveAs('plot_{}.png'.format(fit_type))
