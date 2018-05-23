#!/bin/bash -x

set -eEuo pipefail
set -x

# TODO:
# This is a hacky, hacky script to keep going
# 

function usage {
    echo "Usage: ${0##*/} <USER> <PASSWORD> <VERSION> [COMPONENT]"
}

if [[ $# -lt 3 ]]; then
  >&2 echo "ERROR: invalid parameters"
  usage
fi
USER="${1:-}"
PASSWORD="${2:-}"
VERSION="${3:-}"
COMPONENT="${4:-main}"

API_URL=https://api.bintray.com
BT_PKG_NAME=python-gcg-xenial
BT_SUBJECT="${USER}"

ls -al || true
ls -al deb_dist/ || true

btparams=(
    -H "X-Bintray-Package: ${BT_PKG_NAME}"
    -H "X-Bintray-Version: ${VERSION}"
    -H "X-Bintray-Override: 0"
    -H "X-Bintray-Publish: 1"
    -H "X-Bintray-Debian-Distribution: xenial"
    -H "X-Bintray-Debian-Component: main"
    -H "X-Bintray-Debian-Architecture: all"
)

for f in deb_dist/*.deb; do
  curl -T "$f" -u"${USER}:${PASSWORD}" "${btparams[@]}" \
    "${API_URL}/content/${USER}/deb-oss/pool/p/python-gcg/${f##*/}"
  # PUT /content/:subject/:repo/:file_path
done
