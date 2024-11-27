#! /bin/bash

for i in {000..049}
    do sbatch -J $i_avg_amp_series_02 ../sbatch_scripts/sbatch_run_python_script.sh /scratch/n.beaver/amp_series_02_out/FeGaB_koerner_02_amp_series_$i.out/ amp_series_02/
done
