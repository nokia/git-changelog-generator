#!/bin/bash
set -eEuo pipefail
function usage {
    cat - <<EOF
Usage:

    ${0##*/} USER API_KEY REPO_NAME[/PATH] 
EOF
}

if [[ $# -lt 3 ]]; then
    >&2 echo "ERROR: insufficient number of input parameters"
    usage
    false
fi

USER=${1:-INVALID}
API_KEY=${2:-SILLYPASS}
REPO=${3:-}

curl --fail -X POST -u "${USER}:${API_KEY}" "https://api.bintray.com/calc_metadata/${USER}/${REPO}"

