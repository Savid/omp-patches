#!/usr/bin/env bash
# Build the gateway image from the patched clone in ./upstream.
#
#   scripts/build.sh [image]    # default image: omp-gateway:<version>
#
# The image is the omp release pinned in gateway/package.json, as published,
# with every file the series adds or changes laid over it. build/ holds what
# the Dockerfile copies: the patched files, the release's own copies of the
# files they replace (checked against the published ones) and the files the
# series removes.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
version=$(cat "$root/UPSTREAM")
dir=$root/upstream
image=${1:-omp-gateway:$version}

pinned=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["dependencies"]["@oh-my-pi/pi-coding-agent"])' "$root/gateway/package.json")
if [ "$pinned" != "$version" ]; then
	echo "gateway/package.json pins omp $pinned, UPSTREAM says $version" >&2
	exit 1
fi

build=$root/build
rm -rf "$build"
mkdir -p "$build/overlay" "$build/expected"
: >"$build/removed.txt"

# packages/<dir>/<path> in the clone is node_modules/<npm name>/<path> in the image.
npm_path() {
	local package=${1#packages/}
	package=${package%%/*}
	local name
	name=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$dir/packages/$package/package.json")
	echo "$name/${1#packages/"$package"/}"
}

count=0
while IFS=$'\t' read -r status file; do
	[ -n "$file" ] || continue
	target=$(npm_path "$file")
	case "$status" in
		A | M)
			mkdir -p "$(dirname "$build/overlay/$target")"
			git -C "$dir" show "HEAD:$file" >"$build/overlay/$target"
			if [ "$status" = M ]; then
				mkdir -p "$(dirname "$build/expected/$target")"
				git -C "$dir" show "v$version:$file" >"$build/expected/$target"
			fi
			;;
		D) echo "$target" >>"$build/removed.txt" ;;
		*) echo "unexpected change $status to $file" >&2; exit 1 ;;
	esac
	count=$((count + 1))
done < <(git -C "$dir" diff --no-renames --name-status "v$version" HEAD -- 'packages/*/src/**')

echo "laying $count patched files over omp $version"
docker build --file "$root/gateway/Dockerfile" --tag "$image" \
	--label "org.opencontainers.image.version=$version" "$root"
