#!/usr/bin/env bash
#SBATCH --job-name=shark_denticles_%j
#SBATCH --partition=short
#SBATCH --time=04:00:00
#SBATCH --ntasks=128
#SBATCH --mem=0
#SBATCH --error=denticles_%j.err.txt
#SBATCH --output=denticles_%j.out.txt
#SBATCH --chdir=/scratch/adwarka-denticle/output/

#######################
# Run 'sbatch job.sh' #
#######################

set -e

# Move required files into Parallel Scratch Storage
cp -r /scratch/adwarka-denticle/denticles/simulation/airfoil/ /scratch/adwarka-denticle/airfoil_base/
cd /scratch/adwarka-denticle/airfoil_base/

# Load software (if needed) using module load, e.g.
module load spack
spack env activate foam_env

# Using base STL
rm constant/triSurface/airfoil.stl
mv constant/triSurface/airfoil_base.stl constant/triSurface/airfoil.stl

# Meshing
blockMesh
surfaceFeatureExtract
mv system/snappy.decomposeParDict system/decomposeParDict
decomposePar
mpirun snappyHexMesh -parallel -overwrite
reconstructParMesh -constant
rm -r processor*

# Simulation
mv system/decomposeParDict system/snappy.decomposeParDict
mv system/sim.decomposeParDict system/decomposeParDict
decomposePar
mpirun simpleFoam -parallel
reconstructPar
rm -r processor*
touch foam.foam
# cd ..
# tar -czf airfoil_base.tar.gz airfoil_base/
