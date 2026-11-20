# omp's auth broker and gateway: the omp release pinned in gateway/package.json,
# as published, with the files the patch series adds or changes laid over it.
# Build with scripts/build.sh, which stages build/ from the patched clone.
FROM oven/bun:1.4.4@sha256:1d22548f177f4ff38e0c15baa3c2c46c6c2060ba2d1bc573bb4720b407548f1d
LABEL org.opencontainers.image.source="https://github.com/savid/omp-patches" \
      org.opencontainers.image.description="omp auth broker and gateway with the omp-patches series" \
      org.opencontainers.image.licenses="MIT"
WORKDIR /opt/gateway
COPY gateway/package.json gateway/bun.lock ./
RUN bun install --frozen-lockfile
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
ENV HOME=/state
ENTRYPOINT ["bun", "/opt/gateway/start.ts"]
