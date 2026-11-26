# omp's auth broker and gateway: the omp release pinned in gateway/package.json,
# as published, with the files the patch series adds or changes laid over it.
# Build with scripts/build.sh, which stages build/ from the patched clone.
#
# Multi-arch without emulation: everything that runs (install, checks) runs on
# the build host's CPU, installing the target's native package
# (@oh-my-pi/pi-natives-linux-<cpu>); the target stage only copies files.
FROM --platform=$BUILDPLATFORM oven/bun:1.4.4@sha256:1d22548f177f4ff38e0c15baa3c2c46c6c2060ba2d1bc573bb4720b407548f1d AS gateway
ARG TARGETARCH
WORKDIR /opt/gateway
COPY gateway/package.json gateway/bun.lock ./
RUN case "$TARGETARCH" in \
      amd64) cpu=x64 ;; \
      arm64) cpu=arm64 ;; \
      *) echo "unsupported TARGETARCH $TARGETARCH" >&2; exit 1 ;; \
    esac \
    && bun install --frozen-lockfile --os=linux --cpu="$cpu" \
    && test -d "node_modules/@oh-my-pi/pi-natives-linux-$cpu"
# A patched file replaces the release's own: refuse to build when the published
# copy is not the one the patch was made against.
RUN --mount=type=bind,source=build/expected,target=/tmp/expected \
    cd /tmp/expected && find . -type f | while read -r file; do \
      cmp -s "$file" "/opt/gateway/node_modules/$file" \
        || { echo "published ${file#./} is not the release tag's" >&2; exit 1; }; \
    done
COPY build/overlay/ ./node_modules/
RUN --mount=type=bind,source=build/removed.txt,target=/tmp/removed.txt \
    while read -r file; do rm -f "node_modules/$file"; done < /tmp/removed.txt
COPY gateway/start.ts ./start.ts

FROM oven/bun:1.4.4@sha256:1d22548f177f4ff38e0c15baa3c2c46c6c2060ba2d1bc573bb4720b407548f1d
LABEL org.opencontainers.image.source="https://github.com/savid/omp-patches" \
      org.opencontainers.image.description="omp auth broker and gateway with the omp-patches series" \
      org.opencontainers.image.licenses="MIT"
WORKDIR /opt/gateway
COPY --from=gateway /opt/gateway/ ./
ENV HOME=/state
ENTRYPOINT ["bun", "/opt/gateway/start.ts"]
