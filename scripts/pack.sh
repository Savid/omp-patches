#!/usr/bin/env bash
# Pack the patched @oh-my-pi/pi-ai from ./upstream as a tarball, for projects
# that install it by URL from a release.
#
#   scripts/pack.sh [destination]    # default: dist/
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
dest=$(mkdir -p "${1:-$root/dist}" && cd "${1:-$root/dist}" && pwd)
(cd "$root/upstream/packages/ai" && bun pm pack --quiet --destination "$dest" >/dev/null)
(cd "$dest" && sha256sum ./*.tgz >SHA256SUMS)
ls "$dest"
