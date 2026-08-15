#!/usr/bin/env bash
#SBATCH --job-name=shark_%j
#SBATCH --partition=normal
#SBATCH --time=12:00:00
#SBATCH --ntasks=128
#SBATCH --mem=0
#SBATCH --error=base_%j.err.txt
#SBATCH --output=base_%j.out.txt
#SBATCH --chdir=/scratch/adwarka-denticle/output/

set -e

ANGLES=(0 8 16)

# Load software (if needed) using module load, e.g.
module load spack
spack env activate foam

run_simulation () {
  # Move required files into Parallel Scratch Storage
  mkdir -p "/scratch/adwarka-denticle/simulations/final/angle${1}/base/"
  cp -r "/scratch/adwarka-denticle/denticles/simulation/airfoil_base/." "/scratch/adwarka-denticle/simulations/final/angle${1}/base/"
  cd "/scratch/adwarka-denticle/simulations/final/angle${1}/base/"
  
  # Load STL
  surfaceTransformPoints -rotate-y "$1" /scratch/adwarka-denticle/models/airfoil.stl constant/triSurface/airfoil.stl

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
}

for angle in "${ANGLES[@]}"; do
  echo "Starting simulation for angle $angle..."
  run_simulation $angle
done
