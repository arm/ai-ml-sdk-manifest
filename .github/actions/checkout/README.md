# AI‑ML SDK Checkout Action

Composite GitHub Action to **checkout and sync the Arm AI‑ML SDK** repositories

---

## Why this action?
- One step to grab the whole AI‑ML SDK stack from the manifest
- Cross‑platform: Ubuntu, macOS, Windows
- Optional per‑group checkout to reduce sync time
- Built‑in, declarative overrides for reproducible builds

---

## Quick start
Add this job step to your workflow:

```yaml
jobs:
  checkout_sdk:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout AI‑ML SDK
        uses: arm/ai-ml-sdk-manifest@main
        with:
          repo_groups: all
          overrides: |
            # One per line: owner/repo@ref
            arm/ai-ml-sdk-model-converter@v1.2.3
            myorg/ai-ml-sdk-scenario-runner@feature/x
```

## Inputs

### `repo_groups`
Which repo group to initialize via `repo init -g`.

Allowed values: `all`, `model-converter`, `scenario-runner`, `emulation-layer`, `vgf-lib`

Default: `all`

### `overrides`
Multiline string. Optional **one‑per‑line** overrides in the form:

```
owner/repo@ref
```

- `owner/repo` must be one of the recognized repositories (see below).
- `ref` may be a branch name, tag, or full/short commit SHA. If omitted, `main` is used.
- Inline comments are allowed using `#` (everything after `#` on a line is ignored).
- Blank lines are ignored.

Examples:

```
# Pin two repos to specific refs
arm/ai-ml-sdk-model-converter@v1.2.3
alice/ai-ml-sdk-scenario-runner@feature/x

# Use an exact commit
arm/ai-ml-sdk-vgf-library@abcd1234
```

**Recognized repositories** (and where they live in the workspace):

| Repository slug                         | Path in workspace        |
|-----------------------------------------|--------------------------|
| `ai-ml-sdk-for-vulkan`                  | `.`                      |
| `ai-ml-sdk-model-converter`             | `sw/model-converter`     |
| `ai-ml-sdk-scenario-runner`             | `sw/scenario-runner`     |
| `ai-ml-sdk-vgf-library`                 | `sw/vgf-lib`             |
| `ai-ml-emulation-layer-for-vulkan`      | `sw/emulation-layer`     |

> Note: If a path is missing after sync, it may be filtered out by the chosen `repo_groups`.

---

## Usage patterns

### Minimal (defaults)
```yaml
- name: Checkout AI‑ML SDK (defaults)
  uses: arm/ai-ml-sdk-manifest@main
```

### Only the model converter group
```yaml
- name: Checkout model converter
  uses: arm/ai-ml-sdk-manifest@main
  with:
    repo_groups: model-converter
```

### Pin specific repos using overrides
```yaml
- name: Checkout with overrides
  uses: arm/ai-ml-sdk-manifest@main
  with:
    overrides: |
      arm/ai-ml-sdk-model-converter@v1.2.3
      myorg/ai-ml-sdk-scenario-runner@feature/x
```

---

## License

```
SPDX-FileCopyrightText: Copyright 2024-2025 Arm Limited
SPDX-License-Identifier: Apache-2.0
```

