#!/bin/bash -l
#SBATCH --job-name=remap
#SBATCH --output=logs/remap/remap-jid%A-%a.out
#SBATCH --error=logs/remap/remap-jid%A-%a.err
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
nomadic remap -e $expt_dir -c $config -b $SLURM_ARRAY_TASK_ID