#!/bin/bash
#
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --mem=16G
#SBATCH --output=will_fish_%A_%a_stdout.txt
#SBATCH --error=will_fish_%A_%a_stderr.txt
#SBATCH --time=12:00:00
#SBATCH --job-name=will_fish
#SBATCH --mail-user=j.williams@ou.edu
#SBATCH --mail-type=ALL
#SBATCH --chdir=/home/willhr99/rl-spades
#
#SBATCH --array=0-20
#################################################

# load modules
module load python

# switch to virtualenv
#source spades/bin/activate
source activate spades

# install our stuff
pip install -e .

outfile="spades_exp_"
sep="_"
outfile_end=".csv"
outfile=$outfile$SLURM_ARRAY_JOB_ID$sep$SLURM_ARRAY_TASK_ID$outfile_end

# run python code
python gym_spades/envs/spades_env.py $SLURM_ARRAY_TASK_ID /scratch/willhr99/spades $outfile

# clean up
source deactivate

