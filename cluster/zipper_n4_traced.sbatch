#!/bin/bash
# Submit one traced bigelow n=4 SGrobnerTrace run on UCSB's knot cluster.
# Usage:
#   sbatch zipper_n4_traced.sbatch
# Override params at submit time:
#   sbatch --export=ALL,N=3,Q=7,T=11 zipper_n4_traced.sbatch
#
#SBATCH --job-name=zipper_n4_traced
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.err
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=46G
#SBATCH --time=14-00:00:00
#SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_50,TIME_LIMIT_80
#SBATCH --mail-user=YOUR_EMAIL@ucsb.edu

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p logs_and_traces

# Defaults; override via --export=N=...,Q=...,etc at submit time.
export N=${N:-4}
export Q=${Q:-5}
export T=${T:-7}
export PSTR=${PSTR:-2^31-1}
export UNTWIST=${UNTWIST:-bigelow}
export TRACED=${TRACED:-false}

echo "Host:    $(hostname)"
echo "Date:    $(date)"
echo "PWD:     $(pwd)"
echo "Params:  N=$N Q=$Q T=$T PSTR=$PSTR UNTWIST=$UNTWIST TRACED=$TRACED"
echo "GAP:     $(which gap)"
echo "---"

gap -o 42G -K 42G zipper.gap
