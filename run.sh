#! /bin/bash

sbatch -J 00_Copus_freq_series sbatch_scripts/sbatch_copus_freq_series.sh 0 9e9
sbatch -J 01_Copus_freq_series sbatch_scripts/sbatch_copus_freq_series.sh 1 13e9
sbatch -J 02_Copus_freq_series sbatch_scripts/sbatch_copus_freq_series.sh 2 17e9
sbatch -J 03_Copus_freq_series sbatch_scripts/sbatch_copus_freq_series.sh 3 21e9
sbatch -J 04_Copus_freq_series sbatch_scripts/sbatch_copus_freq_series.sh 4 25e9
sbatch -J 05_Copus_freq_series sbatch_scripts/sbatch_copus_freq_series.sh 5 29e9
