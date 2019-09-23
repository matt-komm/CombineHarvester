import os
import sys
import json
import ROOT
import math
import numpy
import scipy.interpolate

name = "llpScan_ctau1_llp1000_lsp800_noda"
dataCard = "/vols/build/cms/mkomm/LLP/CMSSW_8_1_0/src/cards_noda/ctau1_llp1000_lsp800/out.txt"
basePath = "/vols/build/cms/mkomm/LLP/CMSSW_8_1_0/src/"+name


expectedSignalArray = numpy.logspace(-5,1,300)

jobScanArrayCfg = []

for expectedSignal in expectedSignalArray:
    cmdPath = os.path.join(basePath,"signal_%.6f"%(expectedSignal))
    try:
        os.makedirs(cmdPath)
    except:
        pass
        
    jobScanArrayCfg.append({
        "path":cmdPath,
        "cmd": [
            "combine -M MultiDimFit -t -1 --setParameterRanges llpEff=0.01,2.0 -d "+dataCard+" --setParameters r="+("%.6f"%expectedSignal)+" --redefineSignalPOIs llpEff --algo grid --points 1000  --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --fastScan", 
            #"combine -M Significance -t -1 --setParameterRanges llpEff=0,2 -d "+dataCard+" --expectSignal="+("%.6f"%expectedSignal)+" --rMin "+("%.6f"%(-20.*expectedSignal))+" --rMax "+("%.6f"%(20.*expectedSignal))+" --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic"
        ]
    })



def makeSubmitFile(jobArrayCfg,name):
    if len(jobArrayCfg)==0:
        print "No jobs for '"+name+"' -> skip"
        return
    logDir = os.path.join(basePath,'log')
    try:
        os.mkdir(logDir)
    except:
        pass
    submitFile = open(name,"w")#"runCombine.sh","w")
    submitFile.write('''#!/bin/bash
#$ -cwd
#$ -q hep.q
#$ -l h_rt=00:15:00 
#$ -t 1-'''+str(len(jobArrayCfg))+'''
#$ -e '''+logDir+'''/log.$TASK_ID.err
#$ -o '''+logDir+'''/log.$TASK_ID.out
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
        submitFile.write("CMDPATH="+jobCfg["path"]) 
        submitFile.write("; CMDS=(\\\""+jobCfg["cmd"][0]+"\\\"") 
        for cmd in jobCfg["cmd"][1:]:
            submitFile.write(" \\\""+cmd+"\\\"")
        submitFile.write(")\"\n")
    submitFile.write(")\n")

    submitFile.write('''

eval ${JOBS[$SGE_TASK_ID]}
echo "CMDPATH="$CMDPATH
cd $CMDPATH
ls -lh
for cmd in "${CMDS[@]}"
    do
    echo "-----------------------------------------------------"
    echo "command: "$cmd
    echo "-----------------------------------------------------"
    $cmd
    done


date
    ''')
    submitFile.close()
    
makeSubmitFile(jobScanArrayCfg,"runllpEffScan_"+name+".sh")

