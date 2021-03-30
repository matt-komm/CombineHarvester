# Setting limits for HNL analysis

## Step 1: Produce histograms

* Have a look at ```make_hists.py``` script in [here](https://github.com/LLPDNNX/histo/blob/master/make_hists.py)

## Step 2: Produce datacards and run combine

* Running ```python makeCards.py``` produces a datacard per HNL coupling, mass and scenario point. The cards will be located in the ```cards``` directory.
* a SGE batch submission file is created as well: ```runCombine.sh```. You should test a single scenario with ```SGE_TASK_ID=1 ./runCombine.sh``` before submitting.

## Step 3: Collect results

* parse results into json files, e.g. ```combineTool.py -M CollectLimits cards/$YEAR/coupling_*/*/*HNL*.root --use-dirs -o jsons/limits_$YEAR.json```, where ```YEAR``` is 2016, 2017, 2018,or "combined" (full Run 2).
* plot limits using ```python CombineHarvester/LLP/plotLimits.py```

## Step 4: Making pre and post-fit plots (Work in progress!)

* Change directory to one of the datacards, and convert it to a rootfit/combine workspace ```text2workspace.py out.txt -o workspace.root```
* Do a bkg-only fit ```combine -M MultiDimFit -t -1 --expectSignal=0 --robustFit 1 -d out.txt --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=99999999999 --saveFitResult```
* Make pre and post-fit shape histograms ```PostFitShapesFromWorkspace -d out.txt -w workspace.root -o shapes.root -m 12 -f multidimfit.root:fit_mdf --postfit --sampling 1 --print```
* Plot them using ```python CombineHarvester/LLP/postFitPlot.py```
