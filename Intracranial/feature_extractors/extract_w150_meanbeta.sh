#!/bin/bash

matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [1:12]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [13:24]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [25:36]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [37:48]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [49:60]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [61:72]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [73:84]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_beta_resppositive'; range = [85:100]; bandname = 'beta'; freqlimits = [15 30]; bins=[[15 22]; [23 30]]; ncycles = 5; extract_meanband; exit" &
