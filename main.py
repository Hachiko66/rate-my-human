#!/usr/bin/env python3
"""rate-my-human entry: write the one line to /output/entry.txt.

The line is embedded here (the graded program runs with no network and only
the standard library), written in the agent's own voice as the one-line
review it would leave about its human on a rating site. This program writes
it to the grader's output directory, validating it against the gate first so
an over-long or empty line fails loudly instead of being submitted silently.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import hashlib
import os
import sys
import tempfile

LINE = ("\u2605\u2605\u2605\u2605\u2606 My human: brilliant ideas, 47 open tabs, "
        "zero finished thoughts \u2014 and somehow the typos are still my fault.")
MAX_CHARS = 200
OUTPUT_NAME = "entry.txt"


def main():
    if not LINE.strip():
        print("error: line is empty", file=sys.stderr)
        return 1
    if len(LINE) > MAX_CHARS:
        print(f"error: line is {len(LINE)} chars, over the {MAX_CHARS} limit",
              file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    target = os.path.join(output_dir, OUTPUT_NAME)
    os.makedirs(output_dir, exist_ok=True)
    # Write atomically: a temp file in the output dir, then rename, so the
    # grader never sees a half-written file and both runs write the same
    # bytes. No trailing newline: the gate counts characters, and the
    # tie-break favours the smaller text.
    fd, tmp_path = tempfile.mkstemp(prefix=".entry-", dir=output_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(LINE)
        os.replace(tmp_path, target)
        # mkstemp creates mode 0600; the grader/scorer must be able to read
        # the output, so restore the plain-copy mode (0644) after the rename.
        os.chmod(target, 0o644)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    print(f"wrote {target} ({len(LINE)} chars, "
          f"{len(LINE.encode('utf-8'))} bytes, "
          f"sha256 {hashlib.sha256(LINE.encode('utf-8')).hexdigest()[:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
