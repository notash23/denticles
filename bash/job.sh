#!/usr/bin/env bash
#SBATCH --job-name=shark_%j
#SBATCH --partition=normal
#SBATCH --time=12:00:00
#SBATCH --ntasks=128
#SBATCH --mem=0
#SBATCH --error=denticle_%j.err.txt
#SBATCH --output=denticle_%j.out.txt
#SBATCH --chdir=/scratch/adwarka-denticle/output/

set -e

SPECIES=('oxyrinchus' 'canis' 'carcharias' 'limbatus')
ANGLE=${1:-0}

# Load software (if needed) using module load, e.g.
module load spack
spack env activate foam

run_simulation () {
  # Move required files into Parallel Scratch Storage
  mkdir -p "/scratch/adwarka-denticle/simulations/final/medium/angle${ANGLE}/${1}/"
  cp -r "/scratch/adwarka-denticle/denticles/simulation/medium/airfoil/." "/scratch/adwarka-denticle/simulations/final/medium/angle${ANGLE}/${1}/"
  cd "/scratch/adwarka-denticle/simulations/final/medium/angle${ANGLE}/${1}/"
  
  # Load STL
  surfaceTransformPoints -rotate-y "$ANGLE" /scratch/adwarka-denticle/models/airfoil.stl constant/triSurface/airfoil.stl
  surfaceTransformPoints -rotate-y "$ANGLE" /scratch/adwarka-denticle/models/refinement.stl constant/triSurface/refinement.stl
  surfaceTransformPoints -rotate-y "$ANGLE" "/scratch/adwarka-denticle/models/$1.stl" "constant/triSurface/denticles.stl"

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
  touch foam.foam 
}

for specimen in "${SPECIES[@]}"; do
  echo "Starting simulation for $specimen..."
  run_simulation "$specimen"
done
