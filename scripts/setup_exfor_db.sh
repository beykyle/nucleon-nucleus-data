#!/usr/bin/env bash
# Unpack a pre-built x4i3 EXFOR database and export X43I_DATAPATH.
#
# Usage:  source scripts/setup_exfor_db.sh [2025|2024] [db_root]
#
# The pre-built tarballs ship with exfor_tools (external/exfor_tools/), and are
# the output of `x4i3_tools/setup_exfor_db.py --create-x4i3-tarfile`. If the
# database has already been unpacked at <db_root>/X4-<year>-12-31 it is reused.

_nn_year="${1:-2025}"
_nn_db_root="${2:-${NN_CORPORA_DB_ROOT:-$HOME/x4db}}"
_nn_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

_nn_tag="X4-${_nn_year}-12-31"
_nn_target="${_nn_db_root}/${_nn_tag}"

if [ ! -d "${_nn_target}" ]; then
    # fall back to the layout produced by exfor_tools/update_database.sh
    _nn_alt="${_nn_db_root}/unpack_exfor-${_nn_year}/${_nn_tag}"
    if [ -d "${_nn_alt}" ]; then
        _nn_target="${_nn_alt}"
    else
        _nn_tarball="${_nn_repo}/external/exfor_tools/x4i3_${_nn_tag}.tar.gz"
        if [ ! -f "${_nn_tarball}" ]; then
            echo "error: no unpacked database at ${_nn_target} and no tarball at ${_nn_tarball}" >&2
            echo "       build one with external/exfor_tools/update_database.sh" >&2
            return 1 2>/dev/null || exit 1
        fi
        echo "unpacking ${_nn_tarball} -> ${_nn_target}"
        mkdir -p "${_nn_target}"
        tar -xzf "${_nn_tarball}" -C "${_nn_target}"
    fi
fi

if [ ! -f "${_nn_target}/${_nn_tag}" ]; then
    echo "error: ${_nn_target} does not look like an x4i3 database (no ${_nn_tag} marker)" >&2
    return 1 2>/dev/null || exit 1
fi

export X43I_DATAPATH="${_nn_target}"
echo "X43I_DATAPATH=${X43I_DATAPATH}"
