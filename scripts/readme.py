#!/usr/bin/env python3
"""The patch list in README.md, written from the patches' own headers.

    scripts/readme.py           rewrite the list in README.md
    scripts/readme.py --check   fail when README.md is out of date or a header is incomplete
    scripts/readme.py --notes   print the list as release notes
"""

import email
import email.policy
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START, END = "<!-- patches:start -->", "<!-- patches:end -->"
STATUS = re.compile(r"^(Pending|(Submitted|Backport|Inappropriate|Denied) \[.+\])$")
TRAILER = re.compile(r"^[A-Za-z][A-Za-z-]*: ")


def read(path: pathlib.Path) -> dict:
    message = email.message_from_bytes(path.read_bytes(), policy=email.policy.default)
    subject = re.sub(r"^\[PATCH[^\]]*\]\s*", "", " ".join(str(message["Subject"]).split()))
    text = str(message.get_content()) if not message.is_multipart() else ""
    body = text.split("\n---\n", 1)[0].strip().splitlines()
    trailers = []
    while body and TRAILER.match(body[-1]):
        trailers.insert(0, body.pop())
    status = next((t.split(": ", 1)[1].strip() for t in trailers if t.startswith("Upstream-Status: ")), None)
    if status is None or not STATUS.match(status):
        sys.exit(f"{path.name}: needs an `Upstream-Status:` trailer (Pending, Submitted [where], "
                 f"Backport [version], Inappropriate [why] or Denied [why]), not {status!r}")
    description = "\n".join(body).strip()
    if not description:
        sys.exit(f"{path.name}: needs a description of what the patch does and why")
    return {"file": path.name, "number": path.name[:4], "subject": subject, "status": status,
            "description": description}


def patches() -> list:
    return [read(path) for path in sorted((ROOT / "patches").glob("*.patch"))]


def section(items: list) -> str:
    lines = [START, "", "| # | Patch | Upstream |", "|---|---|---|"]
    for p in items:
        lines.append(f"| {p['number']} | [{p['subject']}](patches/{p['file']}) | {p['status']} |")
    for p in items:
        lines += ["", f"### {p['number']} · {p['subject']}", "", p["description"]]
    lines += ["", END]
    return "\n".join(lines)


def main() -> None:
    items = patches()
    if "--notes" in sys.argv:
        print("\n".join(f"- **{p['subject']}** ({p['status']})" for p in items))
        return
    text = README.read_text()
    if START not in text or END not in text:
        sys.exit(f"README.md needs the {START} and {END} markers")
    head, rest = text.split(START, 1)
    updated = head + section(items) + rest.split(END, 1)[1]
    if "--check" in sys.argv:
        if updated != text:
            sys.exit("README.md's patch list is out of date: run scripts/readme.py")
        return
    README.write_text(updated)


if __name__ == "__main__":
    main()
