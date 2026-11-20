#!/usr/bin/env bash
# Check and test the patched clone in ./upstream (see scripts/apply.sh).
#
#   scripts/test.sh
#
# Runs lint, format and type checks for every package the series touches, the
# tests the series adds or changes, and the suites around what it patches.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
version=$(cat "$root/UPSTREAM")
dir=$root/upstream

# The suites around what the series patches, beside the tests it changes itself.
suites=(
	"packages/ai/test/auth-*.test.ts"
	"packages/ai/test/anthropic-message-thread*.test.ts"
	"packages/coding-agent/test/*auto-reset*.test.ts"
	"packages/coding-agent/test/auth-gateway*.test.ts"
)

cd "$dir"
bun install --frozen-lockfile >/dev/null

# The native addon from the release, so nothing is compiled.
case "$(uname -m)" in
	x86_64) arch=x64 ;;
	aarch64 | arm64) arch=arm64 ;;
	*) echo "unsupported architecture $(uname -m)" >&2; exit 1 ;;
esac
natives=$(mktemp -d)
(cd "$natives" && npm pack --silent "@oh-my-pi/pi-natives-linux-$arch@$version" >/dev/null && tar -xzf ./*.tgz)
mkdir -p packages/natives/native
cp "$natives"/package/*.node packages/natives/native/
rm -rf "$natives"

changed=$(git diff --name-only "v$version" HEAD)
packages=$(echo "$changed" | grep -o '^packages/[^/]*' | sort -u)
for package in $packages; do
	echo "== check $package"
	(cd "$package" && bun run check)
done

shopt -s nullglob
tests=$(
	{
		echo "$changed" | grep -E '^packages/[^/]+/test/.*\.test\.ts$' || true
		for pattern in "${suites[@]}"; do
			# shellcheck disable=SC2086 # the pattern is a glob
			printf '%s\n' $pattern
		done
	} | sort -u
)
for package in $packages; do
	files=$(echo "$tests" | grep "^$package/" | sed "s|^$package/||" || true)
	[ -n "$files" ] || continue
	echo "== test $package"
	# shellcheck disable=SC2086 # one argument per file
	(cd "$package" && bun test $files)
done
