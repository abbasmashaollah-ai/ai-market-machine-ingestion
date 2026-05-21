# Repository Hygiene

This repository keeps source files, architecture docs, and narrowly scoped runtime code only.

## Ignored Artifacts

The repository ignores common local and generated artifacts, including:

- Python bytecode and cache directories
- test and lint caches
- local virtual environments
- local environment files
- OS metadata files

## Tracked Artifact Rule

Generated Python cache artifacts must not be committed. If they become tracked, remove them from Git tracking only and keep the source files intact.

## Hygiene Expectations

- keep source control focused on hand-authored code and documentation
- do not check in runtime caches
- do not check in local environment files
- keep documentation aligned with structural changes
