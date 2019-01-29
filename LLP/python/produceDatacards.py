import os
import sys
import json
import ROOT
import CombineHarvester.CombineTools.ch as ch

    
def makeDatacard(cats,ctau,signalProc,histPath,outputPath,systematics=[]):
    print "Producing datacards for signal '"+signalProc+"' under '"+outputPath+"'"
    if os.path.exists(outputPath):
        pass
    else:
        os.makedirs(outputPath)
        
    cb = ch.CombineHarvester()
    #cb.SetVerbosity(3)
    cb.AddProcesses(era=["13TeV2016"],procs=["WJets","st","ttbar","ZNuNu"],bin=cats.values(),signal=False)
    
    #add signal only to region 'D'
    cb.AddProcesses(era=["13TeV2016"],procs=[signalProc],bin=[cats['D']],signal=True)

    cb.cp().AddSyst(cb,"lumi_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.026))
    #cb.cp().process(['QCDHT']).AddSyst(cb,"qcd_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.2))
    cb.cp().process(['WJets']).AddSyst(cb,"wzjets_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.2))
    cb.cp().process(['st','ttbar']).AddSyst(cb,"topbkg_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.2))
    cb.cp().process(['ZNuNu']).AddSyst(cb,"ZNuNu_$ERA","lnN",ch.SystMap("era")(["13TeV2016"],1.2))
    
    
        
    for syst in systematics:
        cb.cp().AddSyst(cb,syst, "shape", ch.SystMap("era")(["13TeV2016"],1.0))
        
    cb.cp().ExtractShapes(
           os.path.join(histPath,"hists_%s.root"%ctau),
          "$BIN_$PROCESS",
          "$BIN_$PROCESS_$SYSTEMATIC")
          
    '''
    proc = ch.Process()
    proc.set_process('QCD')
    proc.set_bin('llpA')
    proc.set_era('13TeV2016')
    proc.set_rate(1)
    hist = ROOT.TH1F("qcdHist","",13,-0.5,12.5)
    hist.Fill(3)
    hist.SetDirectory(0)
    proc.set_shape(hist,True)
    cb.InsertProcess(proc)
    cb.cp().bin(['llpA']).process(['QCD']).AddSyst(cb,'qcd_$BIN',"rateParam",ch.SystMap("era")(["13TeV2016"],0.))
    '''
    met = ROOT.RooRealVar("met","E_{T}^{miss}",-0.5,12.5)
    bin1 = ROOT.RooRealVar("bkg_SR_bin1","Background yield in signal region, bin 1",10,0,10**6)
    bin2 = ROOT.RooRealVar("bkg_SR_bin2","Background yield in signal region, bin 2",10,0,10**6)
    bin3 = ROOT.RooRealVar("bkg_SR_bin3","Background yield in signal region, bin 3",10,0,10**6)
    bin4 = ROOT.RooRealVar("bkg_SR_bin4","Background yield in signal region, bin 4",10,0,10**6)
    bkg_SR_bins = ROOT.RooArgList()
    bkg_SR_bins.add(bin1)
    bkg_SR_bins.add(bin2)
    bkg_SR_bins.add(bin3)
    bkg_SR_bins.add(bin4)
    hist = ROOT.TH1F("qcdHist","",13,-0.5,12.5)
    hist.SetDirectory(0)
    p_bkg = ROOT.RooParametricHist ("bkg_SR", "Background PDF in signal region",met,bkg_SR_bins,hist)
    proc = ch.Process()
    proc.set_process('QCD')
    proc.set_bin('llpA')
    proc.set_era('13TeV2016')
    proc.set_pdf(p_bkg)
    cb.InsertProcess(proc)
    '''
    bbFactory = ch.BinByBinFactory()
    bbFactory.SetAddThreshold(0.1)
    #bbFactory.SetMergeThreshold(0.5)
    bbFactory.SetFixNorm(True)
    #bbFactory.SetPoissonErrors(True)
    bbFactory.SetPattern("bb_$BIN_$PROCESS_bin_$#")
    #bbFactory.MergeBinErrors(cb.cp().backgrounds())
    bbFactory.AddBinByBin(cb.cp().process(['WJets','st','ttbar','ZNuNu']), cb)
    '''

    #cb.PrintAll()

    cb.cp().WriteDatacard(
        os.path.join(outputPath,"out.txt"),
        os.path.join(outputPath,"out.root")
    )
    

#ctauValues = ["0p001","0p01","0p1","1","10","100","1000","10000"]
ctauValues = ["1"]

systematics = ["jes","jer","unclEn","pu","wjetsScale","ttbarScale","stScale","znunuScale"]

categories = {}
for region in ['A','B','C','D']:
    categories[region] = ((len(categories),"llp"+region))
print categories

with open('eventyields.json',) as f:
    genweights = json.load(f)

massesDict = {}
for ctau in ctauValues:
    ctauSampleName = "SMS-T1qqqq_ctau-%s_TuneCUETP8M1_13TeV-madgraphMLM-pythia8"%ctau
    if not massesDict.has_key(ctau):
        massesDict[ctau] = {}
    for signalSample in [ctauSampleName,ctauSampleName+"_extra"]:
        for llpMass in genweights[signalSample].keys():
            for lspMass in genweights[signalSample][llpMass].keys():
                if genweights[signalSample][llpMass][lspMass]["sum"]<10:
                    continue
                if int(llpMass)==int(lspMass):
                    continue
                if not massesDict[ctau].has_key(llpMass):
                    massesDict[ctau][llpMass] = []
                if not lspMass in massesDict[ctau][llpMass]:
                    massesDict[ctau][llpMass].append(lspMass)

basePath = "cards"
histPath = "hists"
if os.path.exists(os.path.join(basePath,'log')):
    pass
else:
    os.makedirs(os.path.join(basePath,'log'))

jobArrayCfg = []
for ctau in ctauValues:
    for llpMass in sorted(massesDict[ctau].keys()):
        for lspMass in massesDict[ctau][llpMass]:
            signalProcess = "ctau%s_llp%s_lsp%s"%(str(ctau),str(llpMass),str(lspMass))
            datacardPath = os.path.join(basePath,signalProcess)
            makeDatacard(
                categories,
                ctau,
                signalProcess,
                histPath,
                datacardPath,
                systematics=systematics
            )
            
            jobArrayCfg.append([datacardPath])
            
            break
        break
    break
            
submitFile = open("runCombine.sh","w")
submitFile.write('''#!/bin/bash
#$ -cwd
#$ -q hep.q
#$ -l h_rt=02:30:00 
#$ -t 1-'''+str(len(jobArrayCfg))+'''
#$ -e '''+os.path.join(basePath,'log')+'''/log.$TASK_ID.err
#$ -o '''+os.path.join(basePath,'log')+'''/log.$TASK_ID.out
hostname
date
source ~/.bashrc
cd /vols/build/cms/mkomm/LLP/CMSSW_8_1_0/src
eval `scramv1 runtime -sh`
''')

submitFile.write("JOBS=(\n")
submitFile.write(" \"pseudo job\"\n")
for jobCfg in jobArrayCfg:
    submitFile.write(" \"")
    for opt in jobCfg:
        submitFile.write(" "+opt)
    submitFile.write("\"\n")
submitFile.write(")\n")

submitFile.write('''
echo ${JOBS[$SGE_TASK_ID]}
cd ${JOBS[$SGE_TASK_ID]}
#combine -M FitDiagnostics --plots --saveWithUncertainties -t -1 -d out.txt
#combine -M MultiDimFit --saveFitResult -t -1 -d out.txt

#for estimating LEE
#(note: for some weirdness toys>1000 are failing)
#for i in 12 23 34 45 56 67 78 89 90 91 
#for i in 12 23
for i in 12 23 34 45 56 67 78 89 90 91 
    do
    #note: do not use option '--saveToys' as this will store something else in 'limit' branch
    combine -M Significance -t 1000 -s '12'$i'56'$i --maxTries 5 --expectSignal=0 -d out.txt
    done

#expected impacts
text2workspace.py -m 120 out.txt -o workspace.root
combineTool.py -M Impacts -d workspace.root -m 120 --robustFit 1 --doInitialFit -t -1 --expectSignal=1 
combineTool.py -M Impacts -d workspace.root -m 120 --robustFit 1 --doFits -t -1 --expectSignal=1
combineTool.py -M Impacts -d workspace.root -m 120 -o impacts.json
plotImpacts.py -i impacts.json -o impacts

#expected limits
combine -M AsymptoticLimits --rAbsAcc 0.000001 --X-rtd MINIMIZER_MaxCalls=99999999999 -t -1 -d out.txt

date
''')
submitFile.close()


