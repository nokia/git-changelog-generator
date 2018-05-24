#!/bin/bash
# set -eEuo pipefail

# $1 - user
# $2 - password
# $3 - version
# $4 - ignored for RPM; DEB: component

# TODO: turn this into proper deploy scripts

if [[ -n "${DEBUG:-}" ]]; then
    opts="-x"
fi

dir=$(dirname "$(readlink -f "$0")")

bash ${opts:-} "${dir}/deploy_rpm.bash" "$@"
bash ${opts:-} "${dir}/deploy_deb.bash" "$@"

# This in theory is not needed, bintray should should refresh
# the repository metadata on its own. There were cases though when it didn't
# hence an explicit request to do so
bash ${opts:-} "${dir}/calc_metadata.bash" "$1" "$2" "$1" "deb-oss"
bash ${opts:-} "${dir}/calc_metadata.bash" "$1" "$2" "$1" "yum-oss"
