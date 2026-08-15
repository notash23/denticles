#!/usr/bin/env bash
#SBATCH --job-name=paraviz
#SBATCH --partition=short
#SBATCH --time=4:00:00
#SBATCH --ntasks=64
#SBATCH --mem=0

module load spack
spack env activate paraview
spack add paraview+mpi~qt+python
spack compiler find
spack install %gcc
spack env deactivate
spack env activate foam
spack add openfoam
spack install
