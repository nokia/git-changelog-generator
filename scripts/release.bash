#!/bin/bash

set -eEuo pipefail

# TODO; more available arguments for this script
# instead of hardcoded values

function show_help {
    cat - <<HEREDOC
Usage:

    ${0##*/} -v VERSION

    where:
        -d            - debug mode
        RPM_LIFECYCLE - the label identyfuing repository
                        (e.g. stable, testing, unstable). Defaults to 'dev'.
        DEB_COMPONENT - component within the Debian repository;
                        (e.g. stable, testing, unstable). Defaults to 'dev'.

HEREDOC
}

function assert_vars_set {
    declare n
    for n in "$@"; do
        if [[ -n "$n" ]] && [[ -z "${!n:-}" ]]; then
            >&2 show_help
            >&2 echo "ERROR: value for ${n} was not provided"
            exit 1
        else
            if [[ -n ${extra_params:-} ]]; then
                >&2 echo "DEBUG: ${n}=${!n:-}"
            fi
        fi
    done
}

declare version
declare extra_params=
declare root=$(git rev-parse --show-toplevel)

while [[ $# -gt 0 ]]; do
    declare opt="$1"
    shift
    case "$opt" in
    -h)
        show_help
        exit 0
        ;;
    -d) extra_params="-d"
        ;;
    -v) version=${1:-}
        shift
        ;;
    esac
done

assert_vars_set version root

version_static=$(<"$root"/version.txt)
if [[ "$version" != "$version_static" ]]; then
    >&2 cat - <<EOF
ERROR: the version you provided doesn't match the version you provided.

You ask why we then ask for the version?
a) to make it your conscious decision
b) because the version might have been released already before
EOF
fi

git tag -a -m "Version ${version}" "${version}"
git push --tags origin refs/tags/"${version}"

echo "Release ${version} triggered, check " \
     "https://travis-ci.org/nokia/git-changelog-generator status in a  " \
    "while (or wait for the notification e-mail)."
