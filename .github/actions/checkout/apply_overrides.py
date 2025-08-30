#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2024-2025 Arm Limited
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import re
import shlex
import subprocess
import sys

REPO_DIRS = {
    "ai-ml-sdk-for-vulkan": ".",
    "ai-ml-sdk-model-converter": "sw/model-converter",
    "ai-ml-sdk-scenario-runner": "sw/scenario-runner",
    "ai-ml-sdk-vgf-library": "sw/vgf-lib",
    "ai-ml-emulation-layer-for-vulkan": "sw/emulation-layer",
}


def run(cmd, cwd):
    print("+", " ".join(shlex.quote(x) for x in cmd))
    p = subprocess.run(cmd,
                       cwd=cwd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,
                       text=True)
    if p.stdout:
        sys.stdout.write(p.stdout)
    return p.returncode, p.stdout or ""


def check_call(cmd, cwd):
    print("+", " ".join(shlex.quote(x) for x in cmd))
    subprocess.check_call(cmd, cwd=cwd)


def ensure_override_remote(dir_path: pathlib.Path, url: str) -> None:
    check_call(["git", "remote", "add", "override", url], cwd=dir_path)


def resolve_ref(dir_path: pathlib.Path, ref: str) -> str | None:
    code, _ = run([
        "git", "rev-parse", "--verify", "--quiet",
        f"refs/remotes/override/{ref}"
    ],
                  cwd=dir_path)
    if code == 0:
        return f"override/{ref}"
    code, _ = run(
        ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        cwd=dir_path)
    if code == 0:
        return ref
    return None


def apply_override(owner, repo, ref):
    if repo not in REPO_DIRS:
        print(f"Skip {owner}/{repo}@{ref}: unrecognized repo")
        return

    dir_path = pathlib.Path(REPO_DIRS[repo])
    if not dir_path.exists():
        print(
            f"Skip {repo}: path not found '{dir_path}' (possibly filtered by repo_groups)"
        )
        return
    if not (dir_path / ".git").exists():
        print(f"Not a git repo at '{dir_path}'", file=sys.stderr)
        sys.exit(1)

    url = f"https://github.com/{owner}/{repo}.git"
    ensure_override_remote(dir_path, url)
    check_call(["git", "fetch", "--tags", "--force", "override"], cwd=dir_path)

    target = resolve_ref(dir_path, ref)
    if target is None:
        print(f"Ref not found for {repo}: '{ref}'", file=sys.stderr)
        _code, _out = run(["git", "show-ref", "--heads", "--tags"],
                          cwd=dir_path)
        sys.exit(2)

    check_call(["git", "reset", "--hard", target], cwd=dir_path)
    print(f"Override applied to {repo} at '{dir_path}' -> {target}")


_SPEC_RE = re.compile(
    r'^\s*(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)(?:@(?P<ref>[^#\s]+))?\s*$'
)


def parse_and_apply(overrides_text: str) -> None:
    text = overrides_text or ""
    parsed_specs: list[tuple[str, str, str, int]] = []

    for line_no, raw in enumerate(text.splitlines(), 1):
        original = raw
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # strip inline comments: owner/repo@ref # note
        if "#" in line:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
        m = _SPEC_RE.match(line)
        if not m:
            print(f"Skip invalid override on line {line_no}: '{original}'")
            continue
        owner = m.group("owner")
        repo = m.group("repo")
        ref = m.group("ref") or "main"
        if repo not in REPO_DIRS:
            print(f"Skip unknown repo on line {line_no}: '{repo}'")
            continue
        parsed_specs.append((owner, repo, ref, line_no))

    if not parsed_specs:
        print("No valid overrides provided. Skipping.")
        return

    for idx, (owner, repo, ref, line_no) in enumerate(parsed_specs):
        apply_override(owner, repo, ref)


if __name__ == "__main__":
    parse_and_apply(os.environ.get("OVERRIDES", ""))
