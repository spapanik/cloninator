# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Changed

- Changed clone progress messages to use 🟡 while work is in progress and 🟢
  only after cloning, remote setup, and post-checkout commands all succeed
- Changed `generate` output filenames to start with `new_repos_`, or the
  repository group name when using `--split-groups`

### Fixed

- Added clear 🔴 error reporting when repository setup fails
- Made `clone` stop at the first repository failure and exit with status code `1`

## [0.2.0] - 2026-06-29

### Added

- Added a cli flag to print the version
- Added a cli flag to control verbosity
- Added python 3.10 support

### Changed

- Changed subcommands to be passed without the double dash

## [0.1.0] - 2024-03-22

### Added

- Added a command to clone the repos from the config
- Added a command to generate config from the existing repos

[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[Unreleased]: https://github.com/spapanik/cloninator/compare/v0.2.0...main
[0.2.0]: https://github.com/spapanik/cloninator/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/spapanik/cloninator/releases/tag/v0.1.0
