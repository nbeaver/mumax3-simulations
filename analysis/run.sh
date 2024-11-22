#! /bin/bash

#sbatch ../sbatch_scripts/sbatch_run_python_script.sh --debug ../my_mx3_files/FeGaB_koerner_01_B_series_001.out/ B_series_01/
for i in {001..026} ; do sbatch ../sbatch_scripts/sbatch_run_python_script.sh ../my_mx3_files/FeGaB_koerner_01_B_series_${i}.out B_series_01/ ; done
for i in {001..020} ; do sbatch ../sbatch_scripts/sbatch_run_python_script.sh ../my_mx3_files/FeGaB_koerner_01_amp_series_${i}.out amp_series_01/ ; done
