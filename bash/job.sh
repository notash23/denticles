#!/usr/bin/env bash
#SBATCH --job-name=shark_denticles
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH --ntasks=128
#SBATCH --mem=0
#SBATCH --error=denticles_%j.err.txt
#SBATCH --output=denticles_%j.out.txt
#SBATCH --chdir=/scratch/adwarka-denticle/output/

#######################
# Run 'sbatch job.sh' #
#######################

# Move required files into Local Scratch Storage
cp -r /scratch/adwarka-denticle/denticles/simulation/airfoil/ /scratch/adwarka-denticle/
cd /scratch/adwarka-denticle/airfoil/

# Load software (if needed) using module load, e.g.
module load spack
spack env activate foam_env

# Meshing
blockMesh
surfaceFeatureExtract
mv system/snappy.decomposeParDict system/decomposeParDict
decomposePar
mpirun snappyHexMesh -parallel -overwrite
reconstructParMesh -constant
rm -r processor*
mv system/snappy.decomposeParDict system/decomposeParDict
mv system/sim.decomposeParDict system/decomposeParDict
decomposePar

# Simulation
mpirun simpleFoam -parallel
reconstructPar -latestTime
touch foam.foam
cd ..
tar -czf airfoil.tar.gz airfoil/
