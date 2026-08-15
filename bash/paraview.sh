#!/usr/bin/env bash
#SBATCH --job-name=paraviz
#SBATCH --partition=short
#SBATCH --time=4:00:00
#SBATCH --ntasks=64
#SBATCH --mem=0

# Run on local computer
# ssh -fN -L 11111:orcaga01:11111 adwarka@login.orca.pdx.edu

module load spack
spack env activate paraview
srun pvserver
