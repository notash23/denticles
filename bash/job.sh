#!/usr/bin/env bash
#SBATCH --job-name=shark_denticles_%j                                        # Give the job a name.
#SBATCH --partition=short                                                    # Use the short partition for quick jobs.
#SBATCH --time=02:00:00                                                      # Two hour time-limit (format HH:MM:SS).
#SBATCH --ntasks=32                                                          # 32 CPU cores.
#SBATCH --mem=0                                                              # All the memory.
#SBATCH --error=denticles_%j.err.txt                                         # Text file for errors.
#SBATCH --output=denticles_%j.out.txt                                        # Text file for output.
#SBATCH --chdir=/scratch/adwarka-denticles/denticles/simulation/airfoil/     # Starting directory.

#######################
# Run 'sbatch job.sh' #
#######################

# Load software (if needed) using module load, e.g.
module load spack
spack env activate foam_env

# Run your program
blockMesh
surfaceFeatureExtract
decomposePar
mpiexec -np 32 snappyHexMesh -parallel # TODO: check if I can overwrite
reconstructParMesh -latestTime 

mv 2/polyMesh/ constant/ # TODO: could use <latestTime> instead of 2
foamListTimes -rm

mpiexec -np 32 simpleFoam -parallel # TODO: I could use --ntasks instead of 32
reconstructPar -latestTime
touch foam.foam
cd ..
tar -czf airfoil.tar.gz airfoil/
