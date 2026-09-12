# Repository Guidelines

## Project Structure & Module Organization

This repository is currently an empty starting point: no source code, tests, assets, or build configuration have been committed. The root contains `.agents/` and `.codex/` directories for agent configuration.

When adding the first implementation, establish a clear layout and document it in `README.md`. Suggested directories are `src/` for reusable code, `tests/` for automated tests, `examples/` for runnable tutorials, and `assets/` for supporting media. Create only directories the implementation needs.

## Build, Test, and Development Commands

No build, test, or local execution commands are configured yet. Do not assume commands such as `npm test`, `pytest`, or `make build` work.

The first implementation should document dependency installation, a minimal runnable example, and the exact validation commands in `README.md`. Pin dependencies using the chosen ecosystem’s manifest and lockfile where supported.

## Coding Style & Naming Conventions

No language, formatter, or linter has been selected. Once selected, use its standard conventions and commit shared formatting configuration. Keep indentation consistent within each file and avoid mixing tabs and spaces. Prefer descriptive filenames and identifiers; name tutorial files by topic rather than temporary labels.

## Testing Guidelines

No testing framework or coverage threshold exists. Add automated tests alongside executable code, covering expected behavior and meaningful failure cases. Use descriptive test names that identify the behavior under test. Keep tests reproducible and document any required hardware, datasets, or environment variables.

## Commit & Pull Request Guidelines

There is no commit history from which to infer a message convention. Use concise, imperative subjects, such as `Add introductory tutorial` or `Document local setup`, and keep each commit focused.

Pull requests should explain the change, list validation performed, and link related issues when applicable. Include screenshots for visual changes and disclose any checks that could not be run.
