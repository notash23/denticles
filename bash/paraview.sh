#!/usr/bin/env bash
#SBATCH --job-name=paraviz
#SBATCH --partition=short
#SBATCH --time=4:00:00
#SBATCH --ntasks=64
#SBATCH --mem=0

# Run on local computer
# ssh -fN -L 11111:orcaga[number]:11111 [username]@login.orca.pdx.edu

set -e

module load spack
spack env activate paraview
srun pvserver

////
sbatch paraview.sh
 then ssh command line on my computer
 open paraview and add server and connect to server
