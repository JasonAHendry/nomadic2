#!/bin/bash -l
#SBATCH --job-name=nbar
#SBATCH --output=logs/nbar/nbar-jid%A-%a.out
#SBATCH --error=logs/nbar/nbar-jid%A-%a.err
#SBATCH --chdir=./
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --array {array_str}
#SBATCH --mem=16GB
#SBATCH --time=23:00:00


# SETTINGS
expt_dir={expt_dir}
config={config}

# LOAD ANACONDA
module load anaconda/3/.2023.03

# ACTIVATE ENVIRONMENT
conda activate nomadic2-fast

# RUN NOMADIC
nomadic map -e $expt_dir -c $config -b $SLURM_ARRAY_TASK_ID
nomadic remap -e $expt_dir -c $config -b $SLURM_ARRAY_TASK_ID
nomadic qcbams -e $expt_dir -c $config -b $SLURM_ARRAY_TASK_ID
nomadic targets -e $expt_dir -c $config -b $SLURM_ARRAY_TASK_ID
nomadic call -e $expt_dir -c $config -m bcftools -b $SLURM_ARRAY_TASK_ID