#!/bin/bash

matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [1:12]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [13:24]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [25:36]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [37:48]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [49:60]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [61:72]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [73:84]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
matlab -nojvm -nodisplay -nosplash -r "indata = 'LFP_bipolar_noscram_artif_brodmann_w150_highgamma_resppositive'; range = [85:100]; bandname = 'highgamma'; freqlimits = [70 150]; bins=[[70 80]; [81 90]; [91 100]; [101 110]; [111 120]; [121 130]; [131 140]; [141 150]]; ncycles = 6; extract_meanband; exit" &
