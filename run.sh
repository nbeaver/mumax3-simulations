#! /bin/bash

for i in {001..020} ; do sbatch sbatch_scripts/"sbatch_FeGaB_koerner_01_amp_series_$i.sh" ; done
