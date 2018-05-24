#!/bin/bash
set -eEuo pipefail
function usage {
    cat - <<EOF
Usage:

    ${0##*/} USER API_KEY [ <USER|ORGANIZATION> [REPO_NAME]]
EOF
}

if [[ $# -lt 2 ]]; then
    >&2 echo "ERROR: insufficient number of input parameters"
    usage
    false
fi

USER=${1:-INVALID}
API_KEY=${2:-SILLYPASS}
SUBJECT=${3:-weakcamel}
REPO=${4:-deb-oss}

curl --fail -X POST -u "${USER}:${API_KEY}" "https://api.bintray.com/calc_metadata/${SUBJECT}/${REPO}"

