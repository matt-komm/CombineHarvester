# Setting limits for LLP analysis

## Step 1: Produce histograms

* Have a look at ```makeHists.py``` script in [here](https://github.com/daiktas/histo/)

## Step 2: Produce datacards and run combine

* Running ```python CombineHarvester/LLP/makeCards.py``` produces a datacard per HNL coupling, mass and scenario point
* a SGE batch submission file is created as well: ```runCombine.sh```. You can test a single scenario with ```SGE_TASK_ID=1 ./runCombine.sh``` before submitting.

## Step 3: Collect results

* parse results into json files ```combineTool.py -M CollectLimits CombineHarvester/LLP/cards/2016/coupling_*/*/*HNL*.root --use-dirs -o limits.json```
* plot limits using ```python CombineHarvester/LLP/plotLimits.py ```

## Step 4: Making pre and post-fit plots (WIP)
* Change directory to one of the datacards, and convert it to a rootfit/combine workspace ```text2workspace.py out.txt -o workspace.root```
* Do a bkg-only fit ```combine -M MultiDimFit -t -1 --expectSignal=0 --robustFit 1 -d out.txt --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 --saveFitResult```
* Make pre and post-fit shape histograms ```PostFitShapesFromWorkspace -d out.txt -w workspace.root -o shapes.root -m 12 -f multidimfit.root:fit_mdf --postfit --sampling 1 --print```
* Plot them using ```python CombineHarvester/LLP/postFitPlot.py```
