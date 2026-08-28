#!/bin/bash --login
#SBATCH -A frib-nodes
#SBATCH --partition general
#SBATCH --nodes 1
#SBATCH --cpus-per-task 8
#SBATCH --time 18:00:00
#SBATCH --mem 48G
#SBATCH --job-name nn-corpora-nb
#SBATCH --output /mnt/home/beyerkyl/jupyter_log/jupyter-notebook-%J.log

# Launch JupyterLab for the nn_corpora curation notebooks on a compute node.
#
#   sbatch scripts/run_jupyter.slurm
#
# Then read the log named above for the ssh tunnel command and the lab URL.

port=9999
node=$(hostname -s)
user=$(whoami)

repo=/mnt/ufs18/rs/reactiontheoryinitiative/nucleon_nucleus_data
cd "${repo}" || exit 1

## environment: uv, not conda/mamba
module purge
export PATH="${HOME}/.local/bin:${PATH}"
command -v uv >/dev/null || { echo "error: uv not on PATH" >&2; exit 1; }

# resolve the pinned environment (incl. the exfor_tools submodule, editable)
uv sync --extra dev || exit 1

# EXFOR database -> X43I_DATAPATH (pass 2024 for the older release)
source scripts/setup_exfor_db.sh "${NN_CORPORA_DB_YEAR:-2025}" || exit 1

# threading controls
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK

cat <<TUNNEL

To connect, from your local machine:

    ssh -N -L ${port}:${node}:${port} ${user}@hpcc.msu.edu

then open the http://127.0.0.1:${port}/... URL printed below.

TUNNEL

# run jupyter lab out of the uv-managed environment
uv run --extra dev jupyter lab --no-browser --port=${port} --ip=${node} notebooks/
