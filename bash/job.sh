#!/usr/bin/env bash
#SBATCH --job-name=shark_denticles_%j
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH --nodes=2 
#SBATCH --ntasks=128
#SBATCH --mem=0
#SBATCH --error=denticles_%j.err.txt
#SBATCH --output=denticles_%j.out.txt
#SBATCH --chdir=/home/adwarka/output/

#######################
# Run 'sbatch job.sh' #
#######################

# Move required files into Local Scratch Storage
cd /tmp/
cp -r /scratch/adwarka-denticle/denticles/simulation/airfoil/ .
cd airfoil

# Load software (if needed) using module load, e.g.
module load spack
spack env activate foam_env

# Meshing
blockMesh
surfaceFeatureExtract
decomposePar
mpirun snappyHexMesh -parallel -overwrite
reconstructParMesh -constant

# Simulation
mpirun simpleFoam -parallel
reconstructPar -latestTime
touch foam.foam
cd ..
tar -czf airfoil.tar.gz airfoil/
