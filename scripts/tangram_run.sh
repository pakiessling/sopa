#!/bin/bash
#SBATCH --job-name=tangram
#SBATCH --output=/mnt/beegfs/sopa/workflow/logs/%j
#SBATCH --mem=40G
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpgpuq
#SBATCH --gres=gpu:a100:1

module purge
module load anaconda3/2020-11

source activate sopa

cd /mnt/beegfs/merfish/sopa/scripts

SP=PATH.h5ad
REF=PATH.h5ad
OUT=PATH.h5ad

python -u _tangram_run.py -sp $SP -sc $REF -o $OUT
