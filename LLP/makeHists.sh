#!/bin/bash
#$ -cwd
#$ -j y
#$ -q hep.q
#$ -l h_vmem=12G
#$ -l h_rt=3:0:0 
#$ -o log/$JOB_ID_$TASK_ID.dat
#$ -t 1-1260

PYTHONUNBUFFERED=TRUE

date
eval "$(/home/hep/vc1117/anaconda3/bin/conda shell.zsh hook)"; conda activate HNL
echo $SGE_TASK_ID

CATS=(mumu_OS mumu_SS ee_OS ee_SS mue_OS mue_SS emu_OS emu_SS mu e)

SGE_TASK_ID=$((SGE_TASK_ID-1))
PROCESS_ID=$((SGE_TASK_ID / 10 + 1))
CAT_ID=$((SGE_TASK_ID % 10))
echo $PROCESS_ID $CAT_ID

PROC=$(awk "NR == $PROCESS_ID" procs.txt)
CAT=${CATS[CAT_ID]}
echo $PROC $CAT

python -u makeHists.py --proc $PROC --category $CAT
date
