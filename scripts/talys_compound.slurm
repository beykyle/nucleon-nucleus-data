#!/bin/bash --login
#SBATCH -A frib-nodes
#SBATCH --partition general-short
#SBATCH --nodes 1
#SBATCH --cpus-per-task 32
#SBATCH --time 4:00:00
#SBATCH --mem 32G
#SBATCH --job-name talys-ce
#SBATCH --output /mnt/home/beyerkyl/talys_log/talys-%J.log

# Compound-elastic TALYS runs (scripts/talys_compound.py run) on a compute node.
#
#   sbatch scripts/talys_compound.slurm                                   # kduq_evaluated, all CE sectors
#   sbatch --export=ALL,SECTORS=neutron_elastic,TARGETS=Fe_0 scripts/talys_compound.slurm
#
# Environment: CORPUS (default kduq_evaluated), SECTORS (space/comma separated; default the three corrected
# sectors), TARGETS (optional file stems), NN_TALYS_DIR (optional: another TALYS build; default external/talys).
# Afterwards, on the login node: talys_compound.py apply / copy, then scripts/build_manifests.py.

repo=/mnt/ufs18/rs/reactiontheoryinitiative/nucleon_nucleus_data
cd "${repo}" || exit 1

module purge
export PATH="${HOME}/.local/bin:${PATH}"
command -v uv >/dev/null || { echo "error: uv not on PATH" >&2; exit 1; }
uv sync --extra dev || exit 1

export NN_TALYS_DIR="${NN_TALYS_DIR:-${repo}/external/talys}"
export TMPDIR="${TMPDIR:-/tmp}/talys_${SLURM_JOB_ID}"
mkdir -p "${TMPDIR}"
export OMP_NUM_THREADS=1

CORPUS="${CORPUS:-kduq_evaluated}"
SECTORS="${SECTORS:-neutron_elastic proton_elastic proton_reaction}"
targets=()
[ -n "${TARGETS:-}" ] && targets=(--targets ${TARGETS//,/ })

echo "NN_TALYS_DIR=${NN_TALYS_DIR} CORPUS=${CORPUS} SECTORS=${SECTORS} TARGETS=${TARGETS:-all} node=$(hostname -s)"
status=0
for s in ${SECTORS//,/ }; do
    echo "== ${s} $(date)"
    uv run python scripts/talys_compound.py run --corpus "${CORPUS}" --sector "${s}" \
        --workers "${SLURM_CPUS_PER_TASK:-8}" "${targets[@]}" || status=1
done
echo "== done $(date)"
rm -rf "${TMPDIR}"
exit ${status}
