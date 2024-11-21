#! /bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=4:00:00
#SBATCH --job-name=FeGaB_B_series
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --kill-on-invalid-dep=yes
#SBATCH --mail-type=ALL
#SBATCH --output=slurm_job_info/%j/slurm-%j.out
module load anaconda3 cuda
LOG=time_out/time_$(date +%F_%s_%N).txt
mkdir -p "time_out"

# Save environment and job information to local directory.
local_dir=./slurm_job_info/${SLURM_JOB_ID}
mkdir -p "${local_dir}"
cp "$0" "${local_dir}"
env > "${local_dir}/env.txt"
echo "$0" > "${local_dir}/info.txt"
echo "$*" >> "${local_dir}/info.txt"

/usr/bin/time --output=${LOG} --verbose \
mumax3 my_mx3_files/FeGaB_koerner_01_B_series_014.mx3

mumax3-convert -numpy my_mx3_files/FeGaB_koerner_01_B_series_014.out/*.ovf
