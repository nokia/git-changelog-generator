#!/bin/bash

set -eEuo pipefail

# TODO; more available arguments for this script
# instead of hardcoded values

function show_help {
    cat - <<HEREDOC
Usage:

    ${0##*/} -u USERNAME -p PASSWORD -v VERSION -r RPM_LIFECYCLE -c DEB_COMPONENT [-d]

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

declare user
declare password
declare version
declare rpm_lifecycle
declare deb_component
declare extra_params=
declare deb_repo="deb-oss"
declare yum_repo="yum-oss"

while [[ $# -gt 0 ]]; do
    declare opt="$1"
    shift
    case "$opt" in
    -h)
        show_help
        exit 0
        ;;
    -d) opts="-x"
        extra_params="-d"
        ;;
    -u) user=${1:-}
        shift
        ;;
    -p) password=${1:-}
        shift
        ;;
    -v) version=${1:-}
        shift
        ;;
    -r) rpm_lifecycle=${1:-dev}
        shift
        ;;
    -c) deb_component=${1:-dev}
        shift
        ;;
    esac
done

assert_vars_set user password version rpm_lifecycle deb_component

dir=$(dirname "$(readlink -f "$0")")

bash ${opts:-} "${dir}/deploy_deb.bash" -u "$user" -p "$password" -v "$version" -c "$deb_component" $extra_params
bash ${opts:-} "${dir}/deploy_rpm.bash" -u "$user" -p "$password" -v "$version" -r "$rpm_lifecycle" $extra_params

# This in theory is not needed, bintray should should refresh
# the repository metadata on its own. There were cases though when it didn't
# hence an explicit request to do so
bash ${opts:-} "${dir}/calc_metadata.bash" "$user" "$password" "$deb_repo"
bash ${opts:-} "${dir}/calc_metadata.bash" "$user" "$password" "${yum_repo}/${rpm_lifecycle}"
