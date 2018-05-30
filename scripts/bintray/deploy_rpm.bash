#!/bin/bash -x

set -eEuo pipefail
set -x

# TODO:
# This is a hacky, hacky script to keep going
# 

function usage {
    echo "Usage: ${0##*/} <USER> <PASSWORD> <VERSION> [...other ignored]"
}

if [[ $# -lt 3 ]]; then
  >&2 echo "ERROR: invalid parameters"
  usage
fi
USER="${1:-}"
PASSWORD="${2:-}"
VERSION="${3:-}"

API_URL=https://api.bintray.com
BT_PKG_NAME=python-gcg-centos
BT_SUBJECT="${USER}"

btparams=(
    -H "X-Bintray-Package: ${BT_PKG_NAME}"
    -H "X-Bintray-Version: ${VERSION}"
    -H "X-Bintray-Override: 0"
    -H "X-Bintray-Publish: 1"
)

for f in dist/SRPMS/*${VERSION}*.src.rpm dist/RPMS/*/*${VERSION}*.rpm; do
  curl -T "$f" -u"${USER}:${PASSWORD}" "${btparams[@]}" \
  curl --fail -T "$f" -u"${USER}:${PASSWORD}" "${btparams[@]}" \
    "${API_URL}/content/${BT_SUBJECT}/yum-oss/stable/${f##*/}"
  # PUT /content/:subject/:repo/:file_path
done
