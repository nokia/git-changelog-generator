#!/bin/bash

set -eEuo pipefail

# TODO; more available arguments for this script
# instead of hardcoded values

function show_help {
    cat - <<HEREDOC
A trivial release 

Usage:

    ${0##*/} -v VERSION [-n] [-d]

    where:
        -v VERSION    - provide the version to release; mandatory
        -d            - debug mode
        -n            - no-op mode; just print what would be done

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
            if [[ -n ${dbgflag:-} ]]; then
                >&2 echo "DEBUG: ${n}=${!n:-}"
            fi
        fi
    done
}

declare version
declare dbgflag=
declare git_repo_rootdir
declare noop=

if ! command -v git >/dev/null; then
    >&2 echo "ERROR: release of python-gcg requires git command available"
fi
git_repo_rootdir=$(git rev-parse --show-toplevel)

while [[ $# -gt 0 ]]; do
    declare opt="$1"
    shift
    case "$opt" in
    -h)
        show_help
        exit 0
        ;;
    -d) dbgflag="-v"
        export GIT_TRACE=1
        ;;
    -n) noop=echo
        ;;
    -v) version=${1:-}
        shift
        ;;
    esac
done

if [[ -n "$dbgflag" ]]; then
    set -x
fi
assert_vars_set version git_repo_rootdir

[[ $version != $(<"$git_repo_rootdir"/version.txt) ]] &&
    >&2 cat - <<EOF

ERROR: the version you provided doesn't match the version you provided.

      ▞
▐▌▄▄▖▐
▗▖   ▝▖
▝▘    ▝

You ask why we then ask for the version?
a) to make it your conscious decision
b) because the version might have been released already before

Kindly update version.txt and try again.

EOF

$noop git tag ${dbgflag} -a -m "Version ${version}" "${version}"
$noop git push ${dbgflag} --tags origin refs/tags/"${version}"

$noop cat - <<EOF
SUCCESS!

Release ${version} triggered, check
https://travis-ci.org/nokia/git-changelog-generator status
in a while or wait for the notification e-mail

▐  ▌        ▌
▜▀ ▛▀▖▝▀▖▛▀▖▌▗▘ ▌ ▌▞▀▖▌ ▌
▐ ▖▌ ▌▞▀▌▌ ▌▛▚  ▚▄▌▌ ▌▌ ▌
 ▀ ▘ ▘▝▀▘▘ ▘▘ ▘ ▗▄▘▝▀ ▝▀▘

EOF
