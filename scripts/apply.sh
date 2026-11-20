#!/usr/bin/env bash
# Check out omp at a release tag in ./upstream and apply the patch series on top.
#
#   scripts/apply.sh [version]    # default: the version in UPSTREAM
#
# When a patch no longer applies, `git am` stops on it in ./upstream: resolve the
# conflict, `git -C upstream am --continue`, then scripts/save.sh.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
version=${1:-$(cat "$root/UPSTREAM")}
repo=${OMP_UPSTREAM_REPO:-https://github.com/can1357/oh-my-pi.git}
dir=$root/upstream

if [ -d "$dir/.git" ]; then
	git -C "$dir" am --abort >/dev/null 2>&1 || true
	git -C "$dir" fetch --quiet --depth 1 "$repo" "refs/tags/v$version:refs/tags/v$version"
else
	git clone --quiet --depth 1 --branch "v$version" "$repo" "$dir"
fi
git -C "$dir" checkout --quiet --force -B patched "v$version"

shopt -s nullglob
patches=("$root"/patches/*.patch)
if [ ${#patches[@]} -eq 0 ]; then
	echo "no patches to apply" >&2
	exit 1
fi
git -C "$dir" -c user.name="omp-patches" -c user.email="omp-patches@users.noreply.github.com" \
	am --quiet --3way --keep-cr "${patches[@]}"
echo "applied ${#patches[@]} patches to omp $version"
