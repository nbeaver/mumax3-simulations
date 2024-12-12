#! /bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --job-name=zstd_compress_03
#SBATCH --time=24:00:00
#SBATCH --partition=short
#SBATCH --kill-on-invalid-dep=yes
#SBATCH --mail-type=ALL
#SBATCH --output=slurm_job_info/%j/slurm-%j.out
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
tar -C /scratch/n.beaver --use-compress-program zstd -cf /scratch/n.beaver/amp_series_03_out.tar.zst amp_series_03_out/
#tar -C /scratch/n.beaver -czf /scratch/n.beaver/amp_series_03_out.tar.gz amp_series_03_out/
#tar -C /scratch/n.beaver -cJf /scratch/n.beaver/amp_series_03_out.tar.xz amp_series_03_out/
