#!/usr/bin/env bash
# Write the commits in ./upstream on top of the release tag back out as the
# patch series, one file per commit, then regenerate the README's patch list.
#
#   scripts/save.sh
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
version=$(cat "$root/UPSTREAM")
dir=$root/upstream

if [ -d "$dir/.git/rebase-apply" ]; then
	echo "upstream has a patch in progress: finish it with \`git -C upstream am --continue\` first" >&2
	exit 1
fi
if ! git -C "$dir" diff --quiet HEAD; then
	echo "upstream has uncommitted changes: commit them to a patch first" >&2
	exit 1
fi

rm -f "$root"/patches/*.patch
# Unnumbered subjects and a zero From line, so a patch file only changes when
# its own change does.
git -C "$dir" format-patch --quiet --no-numbered --zero-commit --no-signature \
	--base="v$version" --output-directory "$root/patches" "v$version..HEAD"
python3 "$root/scripts/readme.py"
echo "saved $(find "$root/patches" -name "*.patch" | wc -l) patches against omp $version"
