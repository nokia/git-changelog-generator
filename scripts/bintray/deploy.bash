#!/bin/bash
# set -eEuo pipefail

# TODO: turn this into proper deploy scripts

if [[ -n "${DEBUG:-}" ]]; then
    opts="-x"
fi

dir=$(dirname "$(readlink -f "$0")")

bash ${opts:-} "${dir}/deploy_rpm.bash" "$@"
bash ${opts:-} "${dir}/deploy_deb.bash" "$@"
