#! /usr/bin/env sh
# tail --lines=+1 slurm-*.out | less
tail --lines=+1 $(find slurm_job_info/ -maxdepth 2 -name 'slurm-*.out' -print | sort -r) | less -c
