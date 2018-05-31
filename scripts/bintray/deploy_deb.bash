#!/bin/bash -x

set -eEuo pipefail

function show_help {
    cat - <<HEREDOC
Usage:

    ${0##*/} -u USERNAME -p PASSWORD -v VERSION -r RPM_LIFECYCLE -c DEB_COMPONENT [-d]

    where:
        -d            - debug mode
        DEB_COMPONENT - component within the Debian repository;
                        (e.g. stable, testing, unstable). Defaults to 'dev'.

HEREDOC
}

function assert_vars_set {
    for n in "$@"; do
        if [[ -n "$n" ]] && [[ -z "${!n}" ]]; then
            >&2 show_help
            >&2 echo "ERROR: value of ${n} not provided"
            exit 1
        fi
    done
}

declare user
declare password
declare version
declare deb_component

while [[ $# -gt 0 ]]; do
    declare opt="$1"
    case "$opt" in
    -h)
        show_help
        exit 0
        ;;
    -d) opts="-x"
        ;;
    -u) user=${opt:-}
        shift
        ;;
    -p) password=${opt:-}
        shift
        ;;
    -v) version=${opt:-}
        shift
        ;;
    -c) deb_component=${opt:-dev}
        shift
        ;;
    esac
    shift
done

assert_vars_set user password version deb_component

# TODO; more available arguments for this script
# instead of hardcoded values
API_URL=https://api.bintray.com
BT_PKG_NAME=python-gcg-xenial
BT_SUBJECT="${user}"

btparams=(
    -H "X-Bintray-Package: ${BT_PKG_NAME}"
    -H "X-Bintray-Version: ${version}"
    -H "X-Bintray-Override: 0"
    -H "X-Bintray-Publish: 1"
    -H "X-Bintray-Debian-Distribution: xenial"
    -H "X-Bintray-Debian-Component: ${deb_component}"
    -H "X-Bintray-Debian-Architecture: all"
)

set ${opts:-} >/dev/null

for f in deb_dist/*.deb; do
  curl --fail -T "$f" -u"${user}:${password}" "${btparams[@]}" \
    "${API_URL}/content/${BT_SUBJECT}/deb-oss/pool/p/python-gcg/${f##*/}"
  # PUT /content/:subject/:repo/:file_path
done
