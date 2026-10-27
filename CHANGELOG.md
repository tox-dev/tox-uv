# Changelog

<!-- towncrier release notes start -->

<a name="release-1-37-2"></a>

## 1.37.2 (2026-10-27)

<a name="release-1-37-2-documentation"></a>

### Documentation

- Document listing `tox-uv` in the tox `requires` setting ([#400](https://github.com/tox-dev/tox-uv/pull/400)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-37-2-security"></a>

### Security

- Require `uv` 0.13.4 or later in the `tox-uv` meta package, which ships updated root certificates for
  [GHSA-hq85-5cpj-mr62](https://github.com/astral-sh/uv/security/advisories/GHSA-hq85-5cpj-mr62)
  ([#399](https://github.com/tox-dev/tox-uv/pull/399)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-37-1"></a>

## 1.37.1 (2026-10-27)

<a name="release-1-37-1-fixed"></a>

### Fixed

- Fix repository links in the PyPI project description ([#391](https://github.com/tox-dev/tox-uv/pull/391)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-37-0"></a>

## 1.37.0 (2026-10-10)

<a name="release-1-37-0-added"></a>

### Added

- Require Python 3.11 ([#383](https://github.com/tox-dev/tox-uv/pull/383)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-37-0-changes"></a>

### Changes

- Use Python 3.15 by default ([#383](https://github.com/tox-dev/tox-uv/pull/383)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-36-1"></a>

## 1.36.1 (2026-09-29)

<a name="release-1-36-1-fixed"></a>

### Fixed

- Honor `VIRTUALENV_SYSTEM_SITE_PACKAGES` when choosing the default for `system_site_packages`
  ([#376](https://github.com/tox-dev/tox-uv/pull/376)) by [@glaziermag](https://github.com/glaziermag).
- Align the installer with tox 4.59 API changes ([#366](https://github.com/tox-dev/tox-uv/pull/366)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-36-0"></a>

## 1.36.0 (2026-07-21)

<a name="release-1-36-0-added"></a>

### Added

- Support Python 3.15 ([#358](https://github.com/tox-dev/tox-uv/pull/358)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-35-2"></a>

## 1.35.2 (2026-05-05)

<a name="release-1-35-2-fixed"></a>

### Fixed

- Apply constraints to all packages ([#332](https://github.com/tox-dev/tox-uv/pull/332)) by
  [@stephenfin](https://github.com/stephenfin).
- Honor `--recreate` in the lock runner ([#338](https://github.com/tox-dev/tox-uv/pull/338)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-35-1"></a>

## 1.35.1 (2026-04-10)

<a name="release-1-35-1-fixed"></a>

### Fixed

- Honor `UV_FROZEN` and `--frozen` in the lock runner ([#327](https://github.com/tox-dev/tox-uv/pull/327)) by
  [@alexholtz](https://github.com/alexholtz).

<a name="release-1-35-0"></a>

## 1.35.0 (2026-04-09)

<a name="release-1-35-0-added"></a>

### Added

- Handle machine and architecture in Python version specifications ([#321](https://github.com/tox-dev/tox-uv/pull/321))
  by [@griels](https://github.com/griels).

<a name="release-1-35-0-fixed"></a>

### Fixed

- Invalidate installer cache when `UV_*` environment variables change
  ([#325](https://github.com/tox-dev/tox-uv/pull/325)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-34-0"></a>

## 1.34.0 (2026-03-30)

<a name="release-1-34-0-added"></a>

### Added

- Support PEP 723 inline script metadata ([#319](https://github.com/tox-dev/tox-uv/pull/319)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-33-4"></a>

## 1.33.4 (2026-03-12)

<a name="release-1-33-4-fixed"></a>

### Fixed

- Remove the `tox_uv` namespace conflict from the meta distribution ([#314](https://github.com/tox-dev/tox-uv/pull/314))
  by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-33-3"></a>

## 1.33.3 (2026-03-12)

<a name="release-1-33-3-fixed"></a>

### Fixed

- Reject non-Python environment names as interpreter specifications ([#312](https://github.com/tox-dev/tox-uv/pull/312))
  by [@gaborbernat](https://github.com/gaborbernat).
- Resolve environment names ending in digits ([#313](https://github.com/tox-dev/tox-uv/pull/313)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-33-2"></a>

## 1.33.2 (2026-03-10)

<a name="release-1-33-2-fixed"></a>

### Fixed

- Resolve the Python specification when tox provides a fallback path
  ([#308](https://github.com/tox-dev/tox-uv/pull/308)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-33-1"></a>

## 1.33.1 (2026-03-02)

<a name="release-1-33-1-fixed"></a>

### Fixed

- Use `PythonInfo` from its new virtualenv location ([#303](https://github.com/tox-dev/tox-uv/pull/303)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-33-0"></a>

## 1.33.0 (2026-02-25)

<a name="release-1-33-0-fixed"></a>

### Fixed

- Set the virtualenv prompt to the project directory and environment name
  ([#298](https://github.com/tox-dev/tox-uv/pull/298)) by [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-32-1"></a>

## 1.32.1 (2026-02-24)

<a name="release-1-32-1-documentation"></a>

### Documentation

- Show the full README on the tox-uv PyPI page ([#297](https://github.com/tox-dev/tox-uv/pull/297)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-32-0"></a>

## 1.32.0 (2026-02-24)

<a name="release-1-32-0-added"></a>

### Added

- Publish separate `tox-uv` and `tox-uv-bare` distributions ([#296](https://github.com/tox-dev/tox-uv/pull/296)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-31-0"></a>

## 1.31.0 (2026-02-24)

<a name="release-1-31-0-fixed"></a>

### Fixed

- Combine dependencies and dependency groups when resolving with uv ([#294](https://github.com/tox-dev/tox-uv/pull/294))
  by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-30-0"></a>

## 1.30.0 (2026-02-23)

<a name="release-1-30-0-added"></a>

### Added

- Honor `uv_python_preference` ([#264](https://github.com/tox-dev/tox-uv/pull/264)) by
  [@sgaist](https://github.com/sgaist).
- Configure `only_groups` for uv sync ([#293](https://github.com/tox-dev/tox-uv/pull/293)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-30-0-fixed"></a>

### Fixed

- Accept `uv` and `uv-editable` package types in the lock runner ([#287](https://github.com/tox-dev/tox-uv/pull/287)) by
  [@gaborbernat](https://github.com/gaborbernat).
- Handle list-valued uv sources ([#289](https://github.com/tox-dev/tox-uv/pull/289)) by
  [@gaborbernat](https://github.com/gaborbernat).
- Honor `setupdir` when locating `pyproject.toml` ([#290](https://github.com/tox-dev/tox-uv/pull/290)) by
  [@gaborbernat](https://github.com/gaborbernat).
- Resolve a relative work directory with `changedir` ([#291](https://github.com/tox-dev/tox-uv/pull/291)) by
  [@gaborbernat](https://github.com/gaborbernat).
- Use the bundled uv binary for uv sync ([#292](https://github.com/tox-dev/tox-uv/pull/292)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-29-0"></a>

## 1.29.0 (2025-10-09)

<a name="release-1-29-0-added"></a>

### Added

- End support for Python 3.9 ([#255](https://github.com/tox-dev/tox-uv/pull/255)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-29-0-fixed"></a>

### Fixed

- Call the `tox_on_install()` hook in the lock runner ([#241](https://github.com/tox-dev/tox-uv/pull/241)) by
  [@Viicos](https://github.com/Viicos).

<a name="release-1-28-1"></a>

## 1.28.1 (2025-10-09)

<a name="release-1-28-1-fixed"></a>

### Fixed

- Avoid a managed-Python preference collision for issue #253 ([#254](https://github.com/tox-dev/tox-uv/pull/254)) by
  [@CharString](https://github.com/CharString).

<a name="release-1-28-0"></a>

## 1.28.0 (2025-08-14)

<a name="release-1-28-0-fixed"></a>

### Fixed

- Install sourced packages from uv workspaces ([#234](https://github.com/tox-dev/tox-uv/pull/234)) by
  [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-27-0"></a>

## 1.27.0 (2025-08-07)

<a name="release-1-27-0-added"></a>

### Added

- Allow uv sync without the `--locked` flag ([#231](https://github.com/tox-dev/tox-uv/pull/231)) by
  [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-26-2"></a>

## 1.26.2 (2025-07-21)

<a name="release-1-26-2-fixed"></a>

### Fixed

- Honor `skip_missing_interpreters` with uv 0.8 ([#223](https://github.com/tox-dev/tox-uv/pull/223)) by
  [@ziima](https://github.com/ziima).

<a name="release-1-26-1"></a>

## 1.26.1 (2025-06-23)

<a name="release-1-26-1-added"></a>

### Added

- Support Python 3.14 ([#211](https://github.com/tox-dev/tox-uv/pull/211)) by [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-26-1-fixed"></a>

### Fixed

- Recreate a virtualenv when its Python interpreter is missing ([#216](https://github.com/tox-dev/tox-uv/pull/216)) by
  [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-26-0"></a>

## 1.26.0 (2025-05-27)

<a name="release-1-26-0-added"></a>

### Added

- Honor `uv_resolution` in the lock runner ([#205](https://github.com/tox-dev/tox-uv/pull/205)) by
  [@effigies](https://github.com/effigies).
- Support free-threaded Python ([#203](https://github.com/tox-dev/tox-uv/pull/203)) by
  [@khneal](https://github.com/khneal).

<a name="release-1-26-0-fixed"></a>

### Fixed

- Accept both `pip_pre` and `uv_resolution` ([#204](https://github.com/tox-dev/tox-uv/pull/204)) by
  [@effigies](https://github.com/effigies).

<a name="release-1-25-0"></a>

## 1.25.0 (2025-02-21)

<a name="release-1-25-0-added"></a>

### Added

- Delegate packaging and dependency handling to uv ([#180](https://github.com/tox-dev/tox-uv/pull/180)) by
  [@paveldikov](https://github.com/paveldikov).

<a name="release-1-24-1"></a>

## 1.24.1 (2025-02-19)

<a name="release-1-24-0"></a>

## 1.24.0 (2025-02-19)

<a name="release-1-24-0-added"></a>

### Added

- Handle architecture in `base_python` on Windows ([#178](https://github.com/tox-dev/tox-uv/pull/178)) by
  [@schlamar](https://github.com/schlamar).

<a name="release-1-23-2"></a>

## 1.23.2 (2025-02-15)

<a name="release-1-23-2-changes"></a>

### Changes

- Use `--locked` instead of `--frozen` for uv sync ([#177](https://github.com/tox-dev/tox-uv/pull/177)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-23-1"></a>

## 1.23.1 (2025-02-13)

<a name="release-1-23-1-fixed"></a>

### Fixed

- Avoid a crash when an existing environment uses `env_site_packages_dir` in a replacement
  ([#175](https://github.com/tox-dev/tox-uv/pull/175)) by [@gaborbernat](https://github.com/gaborbernat).
- Reinstall wheel projects when using lock files ([#176](https://github.com/tox-dev/tox-uv/pull/176)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-23-0"></a>

## 1.23.0 (2025-02-07)

<a name="release-1-23-0-added"></a>

### Added

- Allow editable, wheel, and skipped package modes in the lock runner
  ([#173](https://github.com/tox-dev/tox-uv/pull/173)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-22-1"></a>

## 1.22.1 (2025-02-05)

<a name="release-1-22-1-fixed"></a>

### Fixed

- Exclude default dependency groups when another group is selected ([#169](https://github.com/tox-dev/tox-uv/pull/169))
  by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-22-0"></a>

## 1.22.0 (2025-02-04)

<a name="release-1-22-0-added"></a>

### Added

- Allow skipping uv sync for lock runner via CLI flag ([#168](https://github.com/tox-dev/tox-uv/pull/168)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-21-1"></a>

## 1.21.1 (2025-02-04)

<a name="release-1-21-1-documentation"></a>

### Documentation

- Fix the README table of contents ([#166](https://github.com/tox-dev/tox-uv/pull/166)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-21-0"></a>

## 1.21.0 (2025-02-04)

<a name="release-1-21-0-fixed"></a>

### Fixed

- Replace broken `with_dev` handling with `no_default_groups` ([#165](https://github.com/tox-dev/tox-uv/pull/165)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-20-2"></a>

## 1.20.2 (2025-01-28)

<a name="release-1-20-2-fixed"></a>

### Fixed

- Avoid false warnings when `UV_CONSTRAINT` is absent ([#162](https://github.com/tox-dev/tox-uv/pull/162)) by
  [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-20-1"></a>

## 1.20.1 (2025-01-22)

<a name="release-1-20-1-fixed"></a>

### Fixed

- Read `UV_PYTHON_PREFERENCE` when `set_env` uses `env_site_packages_dir`
  ([#160](https://github.com/tox-dev/tox-uv/pull/160)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-20-0"></a>

## 1.20.0 (2025-01-21)

<a name="release-1-20-0-added"></a>

### Added

- Honor the `UV_PYTHON_PREFERENCE` environment variable ([#159](https://github.com/tox-dev/tox-uv/pull/159)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-19-1"></a>

## 1.19.1 (2025-01-20)

<a name="release-1-19-1-fixed"></a>

### Fixed

- Select the Python version in the lock runner ([#158](https://github.com/tox-dev/tox-uv/pull/158)) by
  [@evan-lloyd](https://github.com/evan-lloyd).

<a name="release-1-19-0"></a>

## 1.19.0 (2025-01-16)

<a name="release-1-19-0-added"></a>

### Added

- Warn when pip constraints are set without matching uv constraints ([#154](https://github.com/tox-dev/tox-uv/pull/154))
  by [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-18-0"></a>

## 1.18.0 (2025-01-16)

<a name="release-1-18-0-changes"></a>

### Changes

- Prefer the system Python for uv sync ([#148](https://github.com/tox-dev/tox-uv/pull/148)) by
  [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-17-0"></a>

## 1.17.0 (2024-12-30)

<a name="release-1-17-0-added"></a>

### Added

- Support `system_site_packages` like tox ([#147](https://github.com/tox-dev/tox-uv/pull/147)) by
  [@ssbarnea](https://github.com/ssbarnea).

<a name="release-1-16-2"></a>

## 1.16.2 (2024-12-20)

<a name="release-1-16-2-fixed"></a>

### Fixed

- Pass the Python implementation to uv with `-p` ([#143](https://github.com/tox-dev/tox-uv/pull/143)) by
  [@kurtmckee](https://github.com/kurtmckee).

<a name="release-1-16-1"></a>

## 1.16.1 (2024-12-05)

<a name="release-1-16-1-fixed"></a>

### Fixed

- Resolve a PyPy interpreter when the major version is unspecified ([#136](https://github.com/tox-dev/tox-uv/pull/136))
  by [@kurtmckee](https://github.com/kurtmckee).

<a name="release-1-16-0"></a>

## 1.16.0 (2024-10-30)

<a name="release-1-16-0-added"></a>

### Added

- Support dependency groups ([#118](https://github.com/tox-dev/tox-uv/pull/118)) by
  [@gaborbernat](https://github.com/gaborbernat).
- Support `dependency_groups` in TOML configuration ([#119](https://github.com/tox-dev/tox-uv/pull/119)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-16-0-fixed"></a>

### Fixed

- Accept `uv_sync_flags` in TOML configuration ([#119](https://github.com/tox-dev/tox-uv/pull/119)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-16-0-documentation"></a>

### Documentation

- Explain how to temporarily disable tox-uv ([#112](https://github.com/tox-dev/tox-uv/pull/112)) by
  [@hroncok](https://github.com/hroncok).

<a name="release-1-15-0"></a>

## 1.15.0 (2024-10-11)

<a name="release-1-15-0-added"></a>

### Added

- Allow passing extra flags to uv sync ([#107](https://github.com/tox-dev/tox-uv/pull/107)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-14-2"></a>

## 1.14.2 (2024-10-11)

<a name="release-1-14-2-fixed"></a>

### Fixed

- Suppress uv output when tox is not verbose ([#106](https://github.com/tox-dev/tox-uv/pull/106)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-14-1"></a>

## 1.14.1 (2024-10-11)

<a name="release-1-14-1-fixed"></a>

### Fixed

- Pass uv verbosity only when requested by tox ([#105](https://github.com/tox-dev/tox-uv/pull/105)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-14-0"></a>

## 1.14.0 (2024-10-11)

<a name="release-1-14-0-added"></a>

### Added

- End support for Python 3.8 ([#104](https://github.com/tox-dev/tox-uv/pull/104)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-14-0-fixed"></a>

### Fixed

- Match pip verbosity when running uv sync ([#104](https://github.com/tox-dev/tox-uv/pull/104)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-13-1"></a>

## 1.13.1 (2024-10-11)

<a name="release-1-13-0"></a>

## 1.13.0 (2024-09-19)

<a name="release-1-13-0-added"></a>

### Added

- Install project packages with lock files ([#96](https://github.com/tox-dev/tox-uv/pull/96)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-12-1"></a>

## 1.12.1 (2024-09-19)

<a name="release-1-12-1-changes"></a>

### Changes

- Stop installing development dependencies by default ([#95](https://github.com/tox-dev/tox-uv/pull/95)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-12-1-documentation"></a>

### Documentation

- Document dependency handling in the lock runner ([#94](https://github.com/tox-dev/tox-uv/pull/94)) by
  [@hynek](https://github.com/hynek).

<a name="release-1-12-0"></a>

## 1.12.0 (2024-09-19)

<a name="release-1-12-0-added"></a>

### Added

- Support `uv.lock` files ([#91](https://github.com/tox-dev/tox-uv/pull/91)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-11-4"></a>

## 1.11.4 (2024-09-17)

<a name="release-1-11-3"></a>

## 1.11.3 (2024-09-07)

<a name="release-1-11-3-documentation"></a>

### Documentation

- Fix a README link ([#79](https://github.com/tox-dev/tox-uv/pull/79)) by
  [@pmbarrett314](https://github.com/pmbarrett314).
- Fix the discussion link ([#87](https://github.com/tox-dev/tox-uv/pull/87)) by
  [@RomainBrault](https://github.com/RomainBrault).

<a name="release-1-11-2"></a>

## 1.11.2 (2024-08-13)

<a name="release-1-11-2-fixed"></a>

### Fixed

- Resolve conflicting base Python settings ([#77](https://github.com/tox-dev/tox-uv/pull/77)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-11-1"></a>

## 1.11.1 (2024-08-02)

<a name="release-1-11-0"></a>

## 1.11.0 (2024-07-29)

<a name="release-1-11-0-added"></a>

### Added

- Support skipped missing interpreters ([#71](https://github.com/tox-dev/tox-uv/pull/71)) by
  [@RomainBrault](https://github.com/RomainBrault).
- Honor Python installation preferences ([#70](https://github.com/tox-dev/tox-uv/pull/70)) by
  [@RomainBrault](https://github.com/RomainBrault).

<a name="release-1-10-0"></a>

## 1.10.0 (2024-07-26)

<a name="release-1-10-0-added"></a>

### Added

- Accept an absolute path for `base_python` ([#69](https://github.com/tox-dev/tox-uv/pull/69)) by
  [@paveldikov](https://github.com/paveldikov).

<a name="release-1-9-1"></a>

## 1.9.1 (2024-06-27)

<a name="release-1-9-1-fixed"></a>

### Fixed

- Run inside an active uv virtualenv ([#66](https://github.com/tox-dev/tox-uv/pull/66)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-9-0"></a>

## 1.9.0 (2024-05-29)

<a name="release-1-9-0-added"></a>

### Added

- Create uv virtualenvs inside the tox directory and expose uv to them
  ([#59](https://github.com/tox-dev/tox-uv/pull/59)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-9-0-changes"></a>

### Changes

- Remove the `VIRTUAL_ENV=${Python_ROOT_DIR}` workaround ([#57](https://github.com/tox-dev/tox-uv/pull/57)) by
  [@zanieb](https://github.com/zanieb).

<a name="release-1-8-2"></a>

## 1.8.2 (2024-04-30)

<a name="release-1-8-2-fixed"></a>

### Fixed

- Select the requested interpreter ([#53](https://github.com/tox-dev/tox-uv/pull/53)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-1"></a>

## 1.8.1 (2024-04-30)

<a name="release-1-8-1-fixed"></a>

### Fixed

- Check whether an environment exists ([#52](https://github.com/tox-dev/tox-uv/pull/52)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-8-0"></a>

## 1.8.0 (2024-04-29)

<a name="release-1-8-0-added"></a>

### Added

- Add PyPy support ([#51](https://github.com/tox-dev/tox-uv/pull/51)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-7-0"></a>

## 1.7.0 (2024-03-16)

<a name="release-1-7-0-changes"></a>

### Changes

- Pass `sys.executable` to uv when its version matches ([#40](https://github.com/tox-dev/tox-uv/pull/40)) by
  [@ppentchev](https://github.com/ppentchev).

<a name="release-1-6-0"></a>

## 1.6.0 (2024-03-14)

<a name="release-1-6-0-added"></a>

### Added

- Configure `uv_resolution` for tox environments ([#39](https://github.com/tox-dev/tox-uv/pull/39)) by
  [@Stealthii](https://github.com/Stealthii).

<a name="release-1-6-0-fixed"></a>

### Fixed

- Suppress color in `uv pip freeze` output ([#37](https://github.com/tox-dev/tox-uv/pull/37)) by
  [@Stealthii](https://github.com/Stealthii).

<a name="release-1-5-1"></a>

## 1.5.1 (2024-03-07)

<a name="release-1-5-1-fixed"></a>

### Fixed

- Validate the package name before installing an sdist, wheel, or editable project
  ([#33](https://github.com/tox-dev/tox-uv/pull/33)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-5-0"></a>

## 1.5.0 (2024-03-06)

<a name="release-1-5-0-added"></a>

### Added

- Show the uv version in `tox --version` ([#29](https://github.com/tox-dev/tox-uv/pull/29)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-4-0"></a>

## 1.4.0 (2024-02-21)

<a name="release-1-4-0-added"></a>

### Added

- Pass commonly used environment variables to uv ([#26](https://github.com/tox-dev/tox-uv/pull/26)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-2"></a>

## 1.3.2 (2024-02-20)

<a name="release-1-3-2-added"></a>

### Added

- Support Windows ([#19](https://github.com/tox-dev/tox-uv/pull/19)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-1"></a>

## 1.3.1 (2024-02-20)

<a name="release-1-3-1-fixed"></a>

### Fixed

- Use the public uv binary lookup API in uv 0.1.6 ([#25](https://github.com/tox-dev/tox-uv/pull/25)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-0"></a>

## 1.3.0 (2024-02-19)

<a name="release-1-3-0-added"></a>

### Added

- Support major-only Python environment names ([#20](https://github.com/tox-dev/tox-uv/pull/20)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-0-changes"></a>

### Changes

- Enable uv verbose output when tox uses `-vv` ([#20](https://github.com/tox-dev/tox-uv/pull/20)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-3-0-documentation"></a>

### Documentation

- Fix README grammar and typos ([#8](https://github.com/tox-dev/tox-uv/pull/8)) by
  [@edgarrmondragon](https://github.com/edgarrmondragon).
- Document tox as a dependency ([#12](https://github.com/tox-dev/tox-uv/pull/12)) by
  [@hugovk](https://github.com/hugovk).

<a name="release-1-2-0"></a>

## 1.2.0 (2024-02-17)

<a name="release-1-2-0-added"></a>

### Added

- Use uv for packaging environments ([#7](https://github.com/tox-dev/tox-uv/pull/7)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-1-0"></a>

## 1.1.0 (2024-02-16)

<a name="release-1-1-0-changes"></a>

### Changes

- Use uv instead of pip to freeze dependencies ([#5](https://github.com/tox-dev/tox-uv/pull/5)) by
  [@gaborbernat](https://github.com/gaborbernat).
- Stop adding seed packages by default ([#6](https://github.com/tox-dev/tox-uv/pull/6)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-0-2"></a>

## 1.0.2 (2024-02-16)

<a name="release-1-0-2-fixed"></a>

### Fixed

- Include the implementation when building the wheel ([#3](https://github.com/tox-dev/tox-uv/pull/3)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-0-1"></a>

## 1.0.1 (2024-02-16)

<a name="release-1-0-0"></a>

## 1.0.0 (2024-02-16)
