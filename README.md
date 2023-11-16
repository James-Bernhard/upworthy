# Upworthy Archive Python and R scripts

This repository contains the files `preprocessing.py` and `analysis.R`. These are used to preprecess and analyze Upworthy Archive data in the paper "Using a Mixed Effects Model of Multiple A/B Tests to Understand How Different Pronouns in Online News Headlines Affect Click-Through Rate", by James Bernhard. The paper analyzes data from the file `upworthy-archive-confirmatory-packages-03.12.2020.csv`, which can be downloaded from the [Upworthy Archive](https://osf.io/jd64p/). (It is not available in this GitHub repository.)

The Python script `preprocessing.py` reads the file `upworthy-archive-confirmatory-packages-03.12.2020.csv` (placed in the same directory), or any other file specified as the `input_file` toward the top of the script. The script saves the preprocessed output as `df_sentiments.csv` (in the same directory), or as any other file specified as the `output_file` toward the top of the script.

The R script `analysis.R` reads the file `df_sentiments.csv` (from the same directory) and fits the mixed effects model described in the paper. If `save_fitted_model` is set to `TRUE` near the top of the script, then the fitted model will be saved to a file whose filename is specified in `fitted_model_filename` near the top of the script (by default, the filename is `fitted_model.Rdata`). If `load_fitted_model` is set to `TRUE` near the top of the script, then instead of fitting the model, the script will load the fitted model from the file whose filename is specified in `fitted_model_filename`.

For a discussion and interpretation of the mixed effects model, see the paper.

