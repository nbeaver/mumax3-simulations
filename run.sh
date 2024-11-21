#! /bin/bash

for i in {001..026} ; do sbatch  sbatch_scripts/"sbatch_FeGaB_koerner_01_B_series_$i.sh" ; done
