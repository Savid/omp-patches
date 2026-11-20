"""docs/series.svg: how a release is built, drawn from the patch series itself."""

from xml.sax.saxutils import escape

W = 880
SLAB_H, SLAB_GAP, DEPTH = 24, 6, 6
STACK_X, STACK_W = 248, 252
TOP = 64

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# One colour per package a patch changes; anything else wears the last.
PACKAGES = {"ai": "#a78bfa", "coding-agent": "#22d3ee"}
OTHER = "#f472b6"


def colour(package: str) -> str:
    return PACKAGES.get(package, OTHER)


def card(x: float, y: float, w: float, h: float) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="url(#card)" stroke="url(#edge)"/>'
        f'<line x1="{x + 12}" y1="{y + 0.5}" x2="{x + w - 12}" y2="{y + 0.5}" stroke="#ffffff" stroke-opacity=".08"/>'
    )


def label(x: float, y: float, text: str, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{SANS}" font-size="10" font-weight="600" '
        f'letter-spacing="1.6" fill="#64748b">{escape(text)}</text>'
    )


def render(items: list) -> str:
    n = len(items)
    base_y = TOP + n * (SLAB_H + SLAB_GAP)
    bottom = base_y + 32
    mid = (TOP + bottom) / 2
    fail_y = bottom + 34
    h = fail_y + 48
    right_x, right_w = 560, 296
    checks_y, checks_h = TOP, 112
    image_h = 92
    image_y = bottom - image_h

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
        f'aria-labelledby="t">',
        "<title id=\"t\">A new omp release, with the patch series applied in order, checked and tested, "
        "becomes the ghcr.io/savid/omp image; a patch that no longer applies opens an issue.</title>",
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#0a0e17"/><stop offset="1" stop-color="#111827"/></linearGradient>',
        '<linearGradient id="card" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#151c2b"/><stop offset="1" stop-color="#0f1521"/></linearGradient>',
        '<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#334155"/><stop offset="1" stop-color="#1e293b"/></linearGradient>',
        f'<radialGradient id="glow" cx="{STACK_X + STACK_W / 2}" cy="{mid}" r="230" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#7c3aed" stop-opacity=".32"/>'
        '<stop offset=".55" stop-color="#7c3aed" stop-opacity=".08"/>'
        '<stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="glow2" cx="{right_x + right_w / 2}" cy="{image_y + image_h / 2}" r="190" '
        'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#0891b2" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#0891b2" stop-opacity="0"/></radialGradient>',
        '<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#1e293b"/></pattern>',
        '<marker id="head" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#a78bfa"/></marker>',
        '<marker id="headcyan" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#22d3ee"/></marker>',
        '<marker id="headred" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#f87171"/></marker>',
        "</defs>",
        "<style>"
        ".flow{stroke-dasharray:7 7;animation:flow 1.1s linear infinite}"
        ".fail{stroke-dasharray:3 6;animation:flow 1.6s linear infinite}"
        "@keyframes flow{to{stroke-dashoffset:-14}}"
        "@media (prefers-reduced-motion:reduce){.flow,.fail{animation:none}}"
        "</style>",
        f'<rect width="{W}" height="{h}" rx="18" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{h}" rx="18" fill="url(#dots)"/>',
        f'<rect width="{W}" height="{h}" rx="18" fill="url(#glow)"/>',
        f'<rect width="{W}" height="{h}" rx="18" fill="url(#glow2)"/>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="18" fill="none" stroke="#1f2937"/>',
    ]

    # The release.
    rx, rw, rh = 24, 176, 112
    ry = mid - rh / 2
    out += [
        label(rx, TOP - 22, "RELEASE"),
        card(rx, ry, rw, rh),
        f'<path d="M{rx + 20} {ry + 26} h12 l7 7 -7 7 h-12 z" fill="none" stroke="#22d3ee" stroke-width="1.6" '
        'stroke-linejoin="round"/>',
        f'<circle cx="{rx + 26}" cy="{ry + 33}" r="1.8" fill="#22d3ee"/>',
        f'<text x="{rx + 50}" y="{ry + 38}" font-family="{SANS}" font-size="15" font-weight="600" fill="#f1f5f9">'
        "new omp</text>",
        f'<text x="{rx + 20}" y="{ry + 62}" font-family="{MONO}" font-size="11.5" fill="#94a3b8">npm + git tag</text>',
        f'<rect x="{rx + 20}" y="{ry + 76}" width="86" height="22" rx="11" fill="#0e2a33" stroke="#155e75"/>',
        f'<text x="{rx + 63}" y="{ry + 91}" text-anchor="middle" font-family="{SANS}" font-size="11" '
        'font-weight="600" fill="#67e8f9">↻ hourly</text>',
    ]

    # The series, last patch on top, on the release.
    out.append(label(STACK_X, TOP - 22, "PATCH SERIES  ·  GIT AM"))
    slab_w = STACK_W - DEPTH
    for index, patch in enumerate(reversed(items)):
        y = TOP + index * (SLAB_H + SLAB_GAP)
        tint = colour(patch["package"])
        out += [
            f'<rect x="{STACK_X + DEPTH}" y="{y + DEPTH}" width="{slab_w}" height="{SLAB_H}" rx="6" fill="{tint}" '
            'fill-opacity=".18"/>',
            f'<rect x="{STACK_X}" y="{y}" width="{slab_w}" height="{SLAB_H}" rx="6" fill="#121a29" stroke="{tint}" '
            'stroke-opacity=".55"/>',
            f'<rect x="{STACK_X}" y="{y}" width="4" height="{SLAB_H}" rx="2" fill="{tint}"/>',
            f'<text x="{STACK_X + 16}" y="{y + 16.5}" font-family="{MONO}" font-size="12" font-weight="700" '
            f'fill="#e2e8f0">{escape(patch["number"])}</text>',
            f'<text x="{STACK_X + slab_w - 12}" y="{y + 16.5}" text-anchor="end" font-family="{MONO}" '
            f'font-size="11" fill="{tint}">{escape(patch["package"] or "other")}</text>',
        ]
    out += [
        f'<rect x="{STACK_X + DEPTH}" y="{base_y + DEPTH}" width="{slab_w}" height="30" rx="7" fill="#334155" '
        'fill-opacity=".35"/>',
        f'<rect x="{STACK_X}" y="{base_y}" width="{slab_w}" height="30" rx="7" fill="#1e293b" stroke="#475569"/>',
        f'<text x="{STACK_X + slab_w / 2}" y="{base_y + 19.5}" text-anchor="middle" font-family="{SANS}" '
        'font-size="12.5" font-weight="600" fill="#cbd5e1">omp, at the release tag</text>',
    ]

    # Checks, then the image.
    cx = right_x
    out += [
        label(cx, TOP - 22, "CI"),
        card(cx, checks_y, right_w, checks_h),
        f'<text x="{cx + 20}" y="{checks_y + 30}" font-family="{SANS}" font-size="15" font-weight="600" '
        'fill="#f1f5f9">check + test</text>',
    ]
    for row, text in enumerate(("lint + format", "types", "tests of every package touched")):
        y = checks_y + 54 + row * 20
        out += [
            f'<circle cx="{cx + 27}" cy="{y - 4}" r="7" fill="#052e1f" stroke="#10b981"/>',
            f'<path d="M{cx + 23.5} {y - 4} l2.5 2.5 4.5 -5" fill="none" stroke="#34d399" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round"/>',
            f'<text x="{cx + 42}" y="{y}" font-family="{SANS}" font-size="12" fill="#cbd5e1">{escape(text)}</text>',
        ]

    ix, iy = cx + 20, image_y + 16
    cube = (
        f'<path d="M{ix + 11} {iy} l11 6 v13 l-11 6 -11 -6 v-13 z" fill="#0e2a33" stroke="#22d3ee" '
        'stroke-width="1.6" stroke-linejoin="round"/>'
        f'<path d="M{ix} {iy + 6} l11 6 11 -6 M{ix + 11} {iy + 12} v13" fill="none" stroke="#22d3ee" '
        'stroke-width="1.6" stroke-linejoin="round"/>'
    )
    out += [
        label(cx, image_y - 12, "IMAGE"),
        card(cx, image_y, right_w, image_h),
        cube,
        f'<text x="{cx + 54}" y="{image_y + 34}" font-family="{MONO}" font-size="14" font-weight="700" '
        'fill="#f1f5f9">ghcr.io/savid/omp</text>',
    ]
    tx = cx + 20
    for tag in (":<ver>-r<n>", ":<ver>", ":latest"):
        width = 18 + 7 * len(tag)
        out += [
            f'<rect x="{tx}" y="{image_y + 52}" width="{width}" height="22" rx="11" fill="#1a1530" stroke="#5b21b6"/>',
            f'<text x="{tx + width / 2}" y="{image_y + 67}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="11" fill="#c4b5fd">{escape(tag)}</text>',
        ]
        tx += width + 8

    # The flow: release into the series, the series into CI, CI into the image. Each
    # gradient is in user space: a straight line's own box has no height to span.
    stack_right = STACK_X + STACK_W
    arrows = (
        ((rx + rw + 4, mid), (STACK_X - 10, mid), f"M{rx + rw + 4} {mid} H{STACK_X - 10}", "head"),
        (
            (stack_right + 4, TOP + 40),
            (cx - 10, checks_y + checks_h / 2),
            f"M{stack_right + 4} {TOP + 40} C{stack_right + 30} {TOP + 40} {cx - 34} "
            f"{checks_y + checks_h / 2} {cx - 10} {checks_y + checks_h / 2}",
            "head",
        ),
        (
            (cx + right_w / 2, checks_y + checks_h + 4),
            (cx + right_w / 2, image_y - 8),
            f"M{cx + right_w / 2} {checks_y + checks_h + 4} V{image_y - 8}",
            "headcyan",
        ),
    )
    for index, ((x1, y1), (x2, y2), path, head) in enumerate(arrows):
        start, end = ("#a78bfa", "#22d3ee") if head == "headcyan" else ("#22d3ee", "#a78bfa")
        out += [
            f'<linearGradient id="flow{index}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" '
            f'y2="{y2}"><stop offset="0" stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient>',
            f'<path class="flow" d="{path}" stroke="url(#flow{index})" stroke-width="2" fill="none" '
            f'marker-end="url(#{head})"/>',
        ]

    # A patch that no longer applies: an issue instead of a release.
    fx = STACK_X + slab_w / 2
    pill_w = 300
    out += [
        f'<path class="fail" d="M{fx} {bottom + 2} V{fail_y - 6}" stroke="#f87171" stroke-width="1.6" fill="none" '
        'marker-end="url(#headred)"/>',
        f'<rect x="{fx - pill_w / 2}" y="{fail_y}" width="{pill_w}" height="28" rx="14" fill="#2a1215" '
        'stroke="#7f1d1d"/>',
        f'<text x="{fx}" y="{fail_y + 18.5}" text-anchor="middle" font-family="{SANS}" font-size="12" '
        'fill="#fca5a5">a patch no longer applies → GitHub issue</text>',
    ]

    # Which colour is which package.
    lx = cx
    for package in sorted({p["package"] for p in items}, key=lambda name: (name not in PACKAGES, name)):
        tint = colour(package)
        out += [
            f'<rect x="{lx}" y="{fail_y + 8}" width="12" height="12" rx="3" fill="{tint}" fill-opacity=".85"/>',
            f'<text x="{lx + 18}" y="{fail_y + 18.5}" font-family="{MONO}" font-size="11" fill="#94a3b8">'
            f"{escape(package or 'other')}</text>",
        ]
        lx += 30 + 7 * len(package or "other")

    out.append("</svg>")
    return "\n".join(out) + "\n"
