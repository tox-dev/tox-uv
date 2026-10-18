# Changelog

<!-- towncrier release notes start -->

## 1.37.0 (2026-10-10)

### What's Changed

- 👷 ci: pin ubuntu-26.04 and bump dependencies by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/380
- ci: build release packages in parallel by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/382
- feat(python): require 3.11 and default to 3.15 by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/383

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.36.1...1.37.0

## 1.36.1 (2026-09-29)

- Honor `VIRTUALENV_SYSTEM_SITE_PACKAGES` when choosing the default for `system_site_packages`
  ([#376](https://github.com/tox-dev/tox-uv/pull/376)).
- Align the installer with tox 4.59 API changes ([#366](https://github.com/tox-dev/tox-uv/pull/366)).

## 1.36.0 (2026-07-21)

### What's Changed

- Fix flaky na-interpreter test for skip_missing_interpreters default by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/349
- Replace prettier with mdformat and yamlfmt by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/356
- 👷 ci: add Python 3.15 to the test matrix by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/358

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.35.2...1.36.0

## 1.35.2 (2026-05-05)

### What's Changed

- Honor constraints opt for all packages by @stephenfin in https://github.com/tox-dev/tox-uv/pull/332
- 🐛 fix(lock): honor --recreate in uv-venv-lock-runner by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/338

### New Contributors

- @stephenfin made their first contribution in https://github.com/tox-dev/tox-uv/pull/332

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.35.1...1.35.2

## 1.35.1 (2026-04-10)

### What's Changed

- fix(lock-runner): respect UV_FROZEN env var and --frozen in uv_sync_flags by @alexholtz in
  https://github.com/tox-dev/tox-uv/pull/327

### New Contributors

- @alexholtz made their first contribution in https://github.com/tox-dev/tox-uv/pull/327

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.35.0...1.35.1

## 1.35.0 (2026-04-09)

### What's Changed

- Add machine and architecture handling to version spec by @griels in https://github.com/tox-dev/tox-uv/pull/321
- 🐛 fix(installer): invalidate install cache on UV\_\* env var changes by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/325

### New Contributors

- @griels made their first contribution in https://github.com/tox-dev/tox-uv/pull/321

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.34.0...1.35.0

## 1.34.0 (2026-03-30)

### What's Changed

- 🔒 ci(workflows): add zizmor security auditing by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/317
- ✨ feat(runner): add PEP 723 inline script metadata support by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/319

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.33.4...1.34.0

## 1.33.4 (2026-03-12)

### What's Changed

- 🐛 fix(meta): remove tox_uv namespace conflict by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/314

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.33.3...1.33.4

## 1.33.3 (2026-03-12)

### What's Changed

- 🐛 fix(venv): reject non-Python env names as interpreter specs by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/312
- 🐛 fix(venv): resolve env names with trailing digits correctly by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/313

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.33.2...1.33.3

## 1.33.2 (2026-03-10)

### What's Changed

- 🐛 fix(venv): resolve Python spec from env name when tox passes fallback path by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/308

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.33.1...1.33.2

## 1.33.1 (2026-03-02)

### What's Changed

- Move SECURITY.md to .github/SECURITY.md by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/302
- 🐛 fix(venv): use virtualenv PythonInfo from new location by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/303
- Add permissions to workflows by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/299
- Add missing .github config files by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/304
- Standardize .github files to .yaml suffix by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/305

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.33.0...1.33.1

## 1.33.0 (2026-02-25)

### What's Changed

- fix: set venv prompt to be proj_dir[env_name] by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/298

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.32.1...1.33.0

## 1.32.1 (2026-02-24)

### What's Changed

- 📝 docs(meta): use full README for tox-uv PyPI page by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/297

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.32.0...1.32.1

## 1.32.0 (2026-02-24)

### What's Changed

- ♻️ refactor(runner): delegate setup orchestration to parent class by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/295
- ✨ feat(packaging): add monorepo with bare and meta packages by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/296

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.31.0...1.32.0

## 1.31.0 (2026-02-24)

### What's Changed

- 🐛 fix(runner): combine deps and dependency groups for uv_resolution by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/294

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.30.0...1.31.0

## 1.30.0 (2026-02-23)

### What's Changed

- feat: improve handling of uv_python_preference by @sgaist in https://github.com/tox-dev/tox-uv/pull/264
- 🔧 chore(tox): migrate tox.ini to tox.toml by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/284
- Migrate type checking from mypy to ty by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/285
- 🐛 fix(lock-runner): accept uv/uv-editable package types by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/287
- 🐛 fix(installer): handle list-type uv sources by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/289
- 🐛 fix(lock-runner): honor setupdir for pyproject.toml by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/290
- 🐛 fix(venv): resolve relative workdir with changedir by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/291
- 🐛 fix(lock): use bundled uv binary for uv sync by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/292
- ✨ feat(lock): add only_groups config for uv sync by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/293

### New Contributors

- @sgaist made their first contribution in https://github.com/tox-dev/tox-uv/pull/264

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.29.0...1.30.0

## 1.29.0 (2025-10-09)

### What's Changed

- Drop 3.9 support by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/255
- Make sure `tox_on_install()` hook is called in `UvVenvLockRunner._setup_env()` by @Viicos in
  https://github.com/tox-dev/tox-uv/pull/241

### New Contributors

- @Viicos made their first contribution in https://github.com/tox-dev/tox-uv/pull/241

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.28.1...1.29.0

## 1.28.1 (2025-10-09)

### What's Changed

- fix: no-managed-python collision with python-preference (#253) by @CharString in
  https://github.com/tox-dev/tox-uv/pull/254

### New Contributors

- @CharString made their first contribution in https://github.com/tox-dev/tox-uv/pull/254

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.28.0...1.28.1

## 1.28.0 (2025-08-14)

### What's Changed

- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/232
- Bump actions/checkout from 4 to 5 by @dependabot[bot] in https://github.com/tox-dev/tox-uv/pull/235
- chore: use specific github actions runners by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/236
- fix: allow installation of sourced packages from uv workspaces by @ssbarnea in
  https://github.com/tox-dev/tox-uv/pull/234

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.27.0...1.28.0

## 1.27.0 (2025-08-07)

### What's Changed

- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/224
- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/225
- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/227
- Bump actions/download-artifact from 4 to 5 by @dependabot[bot] in https://github.com/tox-dev/tox-uv/pull/229
- fix: add option to avoid addition of --locked to uv sync by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/231
- Enable minimal testing with windows and macOS by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/215

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.26.2...1.27.0

## 1.26.2 (2025-07-21)

### What's Changed

- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/218
- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/219
- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/tox-dev/tox-uv/pull/221
- Support skip_missing_interpreters on uv==0.8.0 (#222) by @ziima in https://github.com/tox-dev/tox-uv/pull/223

### New Contributors

- @ziima made their first contribution in https://github.com/tox-dev/tox-uv/pull/223

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.26.1...1.26.2

## 1.26.1 (2025-06-23)

### What's Changed

- Enable support for python 3.14 by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/211
- Adopt more modern ruff pre-commit hook config by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/213
- Recreate venv if python interpreter is missing by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/216

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.26.0...1.26.1

## 1.26.0 (2025-05-27)

### What's Changed

- fix: Accept both pip_pre and uv_resolution by @effigies in https://github.com/tox-dev/tox-uv/pull/204
- feat: Respect uv_resolution in uv-venv-lock-runner by @effigies in https://github.com/tox-dev/tox-uv/pull/205
- feat: free-threaded python support by @khneal in https://github.com/tox-dev/tox-uv/pull/203

### New Contributors

- @effigies made their first contribution in https://github.com/tox-dev/tox-uv/pull/204
- @khneal made their first contribution in https://github.com/tox-dev/tox-uv/pull/203

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.25.0...1.26.0

## 1.25.0 (2025-02-21)

### What's Changed

- allow to delegate to uv's built-in packaging and dependency handling by @paveldikov in
  https://github.com/tox-dev/tox-uv/pull/180

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.24.1...1.25.0

## 1.24.1 (2025-02-19)

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.24.0...1.24.1

## 1.24.0 (2025-02-19)

### What's Changed

- Handle architecture configuration in base_python on Windows by @schlamar in https://github.com/tox-dev/tox-uv/pull/178

### New Contributors

- @schlamar made their first contribution in https://github.com/tox-dev/tox-uv/pull/178

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.23.2...1.24.0

## 1.23.2 (2025-02-15)

### What's Changed

- Use --locked instead of --frozen for uv sync by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/177

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.23.1...1.23.2

## 1.23.1 (2025-02-13)

### What's Changed

- Fix crash when env already exists and has env_site_packages_dir in replacement by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/175
- Force reinstall of wheel project for lock files by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/176

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.23.0...1.23.1

## 1.23.0 (2025-02-07)

### What's Changed

- Lock mode: allow setting package to editable, wheel or skip by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/173

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.22.1...1.23.0

## 1.22.1 (2025-02-05)

### What's Changed

- Enable no default group flag for uv sync if any group is specified by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/169

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.22.0...1.22.1

## 1.22.0 (2025-02-04)

### What's Changed

- Allow skipping uv sync for lock runner via CLI flag by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/168

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.21.1...1.22.0

## 1.21.1 (2025-02-04)

### What's Changed

- Fix readme table of contents by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/166

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.21.0...1.21.1

## 1.21.0 (2025-02-04)

### What's Changed

- Fix with_dev broken by replacing it with the more generic no_default_groups by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/165

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.20.2...1.21.0

## 1.20.2 (2025-01-28)

### What's Changed

- Avoid false warnings about missing UV_CONSTRAINT variable by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/162

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.20.1...1.20.2

## 1.20.1 (2025-01-22)

### What's Changed

- Fix UV_PYTHON_PREFERENCE reading breaks tox when env_site_packages_dir is in set_env by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/160

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.20.0...1.20.1

## 1.20.0 (2025-01-21)

### What's Changed

- Respect UV_PYTHON_PREFERENCE environment variable by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/159

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.19.1...1.20.0

## 1.19.1 (2025-01-20)

### What's Changed

- Use python version in lock runner by @evan-lloyd in https://github.com/tox-dev/tox-uv/pull/158

### New Contributors

- @evan-lloyd made their first contribution in https://github.com/tox-dev/tox-uv/pull/158

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.19.0...1.19.1

## 1.19.0 (2025-01-16)

### What's Changed

- Improve naming for logger instance by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/155
- Display warning if PIP_CONSTRAINT(S) are defined and UV_CONSTRAINTS not by @ssbarnea in
  https://github.com/tox-dev/tox-uv/pull/154

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.18.0...1.19.0

## 1.18.0 (2025-01-16)

### What's Changed

- Prevent user tox config from affecting tox-uv test runs by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/152
- Make sync prefer system python instead of uv managed by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/148

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.17.0...1.18.0

## 1.17.0 (2024-12-30)

### What's Changed

- Add support for system_site_packages matching tox own behavior by @ssbarnea in
  https://github.com/tox-dev/tox-uv/pull/147

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.16.2...1.17.0

## 1.16.2 (2024-12-20)

### What's Changed

- Always pass the Python implementation to uv's `-p` argument by @kurtmckee in
  https://github.com/tox-dev/tox-uv/pull/143

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.16.1...1.16.2

## 1.16.1 (2024-12-05)

### What's Changed

- Use logger instance instead of ruff by @ssbarnea in https://github.com/tox-dev/tox-uv/pull/128
- Fix `pypyNone` interpreter spec when major version unspecified by @kurtmckee in
  https://github.com/tox-dev/tox-uv/pull/136

### New Contributors

- @ssbarnea made their first contribution in https://github.com/tox-dev/tox-uv/pull/128
- @kurtmckee made their first contribution in https://github.com/tox-dev/tox-uv/pull/136

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.16.0...1.16.1

## 1.16.0 (2024-10-30)

### What's Changed

- Document how to temporarily disable tox-uv by @hroncok in https://github.com/tox-dev/tox-uv/pull/112
- Use dependency groups by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/118
- Fix uv_sync_flags fails in TOML config and add support for dependency_groups by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/119

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.15.0...1.16.0

## 1.15.0 (2024-10-11)

### What's Changed

- Allow passing extra flags to uv sync by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/107

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.14.2...1.15.0

## 1.14.2 (2024-10-11)

### What's Changed

- Fix uv output shows with no verbose flag by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/106

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.14.1...1.14.2

## 1.14.1 (2024-10-11)

### What's Changed

- Fix verbosity flag also passed with single verbose flag to tox by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/105

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.14.0...1.14.1

## 1.14.0 (2024-10-11)

### What's Changed

- Drop 3.8 and uv sync now works in verbose mode same way as pip by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/104

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.13.1...1.14.0

## 1.13.1 (2024-10-11)

### What's Changed

- Tests: In other_interpreter_exe, try python3 -> python3.Y by @hroncok in https://github.com/tox-dev/tox-uv/pull/103

### New Contributors

- @hroncok made their first contribution in https://github.com/tox-dev/tox-uv/pull/103

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.13.0...1.13.1

## 1.13.0 (2024-09-19)

### What's Changed

- Install package support for lock files by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/96

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.12.1...1.13.0

## 1.12.1 (2024-09-19)

### What's Changed

- Document lack of deps for uv-venv-lock-runner by @hynek in https://github.com/tox-dev/tox-uv/pull/94
- Do not install dev dependencies by default by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/95

### New Contributors

- @hynek made their first contribution in https://github.com/tox-dev/tox-uv/pull/94

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.12.0...1.12.1

## 1.12.0 (2024-09-19)

### What's Changed

- Add `uv.lock` support by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/91

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.11.4...1.12.0

## 1.11.4 (2024-09-17)

### What's Changed

- Improve the CI by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/90

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.11.3...1.11.4

## 1.11.3 (2024-09-07)

### What's Changed

- Fix broken link in README.md by @pmbarrett314 in https://github.com/tox-dev/tox-uv/pull/79
- fix: discussion link by @RomainBrault in https://github.com/tox-dev/tox-uv/pull/87

### New Contributors

- @pmbarrett314 made their first contribution in https://github.com/tox-dev/tox-uv/pull/79

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.11.2...1.11.3

## 1.11.2 (2024-08-13)

### What's Changed

- Fix base python conflict by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/77

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.11.1...1.11.2

## 1.11.1 (2024-08-02)

### What's Changed

- Fix CI for new UV by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/74

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.11.0...1.11.1

## 1.11.0 (2024-07-29)

### What's Changed

- Skip missing interpreters by @RomainBrault in https://github.com/tox-dev/tox-uv/pull/71
- Python preference by @RomainBrault in https://github.com/tox-dev/tox-uv/pull/70

### New Contributors

- @RomainBrault made their first contribution in https://github.com/tox-dev/tox-uv/pull/71

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.10.0...1.11.0

## 1.10.0 (2024-07-26)

### What's Changed

- Support base_python passed as absolute path by @paveldikov in https://github.com/tox-dev/tox-uv/pull/69

### New Contributors

- @paveldikov made their first contribution in https://github.com/tox-dev/tox-uv/pull/69

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.9.1...1.10.0

## 1.9.1 (2024-06-27)

### What's Changed

- Fix failure when running within a UV venv activated shell by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/66

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.9.0...1.9.1

## 1.9.0 (2024-05-29)

### What's Changed

- Drop use of `VIRTUAL_ENV=${Python_ROOT_DIR}` workaround by @zanieb in https://github.com/tox-dev/tox-uv/pull/57
- Inline uv venv into the tox folder and expose uv to created env by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/59

### New Contributors

- @zanieb made their first contribution in https://github.com/tox-dev/tox-uv/pull/57

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.8.2...1.9.0

## 1.8.2 (2024-04-30)

### What's Changed

- Fix interpreter by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/53

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.8.1...1.8.2

## 1.8.1 (2024-04-30)

### What's Changed

- Fix environment check by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/52

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.8.0...1.8.1

## 1.8.0 (2024-04-29)

### What's Changed

- Add PyPy support by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/51

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.7.0...1.8.0

## 1.7.0 (2024-03-16)

### What's Changed

- Pass sys.executable to `uv venv` if it is the same version by @ppentchev in https://github.com/tox-dev/tox-uv/pull/40

### New Contributors

- @ppentchev made their first contribution in https://github.com/tox-dev/tox-uv/pull/40

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.6.0...1.7.0

## 1.6.0 (2024-03-14)

### What's Changed

- Ensure uv pip freeze is colorless by @Stealthii in https://github.com/tox-dev/tox-uv/pull/37
- Add uv_resolution as testenv parameter by @Stealthii in https://github.com/tox-dev/tox-uv/pull/39

### New Contributors

- @pre-commit-ci made their first contribution in https://github.com/tox-dev/tox-uv/pull/35
- @Stealthii made their first contribution in https://github.com/tox-dev/tox-uv/pull/37

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.5.1...1.6.0

## 1.5.1 (2024-03-07)

### What's Changed

- Validate package name of sdist/wheel/editable to be installed by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/33

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.5.0...1.5.1

## 1.5.0 (2024-03-06)

### What's Changed

- Add the uv version into the --version by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/29

### New Contributors

- @dependabot made their first contribution in https://github.com/tox-dev/tox-uv/pull/27

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.4.0...1.5.0

## 1.4.0 (2024-02-21)

### What's Changed

- Pass through often used environment variables by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/26

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.3.2...1.4.0

## 1.3.2 (2024-02-20)

### What's Changed

- Support Windows by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/19

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.3.1...1.3.2

## 1.3.1 (2024-02-20)

### What's Changed

- Use uv in CI over pip by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/21
- Do not reinstall uv in CI by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/22
- Fix CI for 0.1.5 by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/23
- Fixes for 0.1.6 by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/25

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.3.0...1.3.1

## 1.3.0 (2024-02-19)

### What's Changed

- Fix grammar and typos in README by @edgarrmondragon in https://github.com/tox-dev/tox-uv/pull/8
- README: tox is a dependency of tox-uv by @hugovk in https://github.com/tox-dev/tox-uv/pull/12
- sdist fixed upstream by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/18
- Support major only Python environments and enable uv verbose mode on 2 or more -v for tox by @gaborbernat in
  https://github.com/tox-dev/tox-uv/pull/20

### New Contributors

- @edgarrmondragon made their first contribution in https://github.com/tox-dev/tox-uv/pull/8
- @hugovk made their first contribution in https://github.com/tox-dev/tox-uv/pull/12

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.2.0...1.3.0

## 1.2.0 (2024-02-17)

### What's Changed

- Use uv for packaging environments too by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/7

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.1.0...1.2.0

## 1.1.0 (2024-02-16)

### What's Changed

- Use uv freeze over pip by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/5
- Disable adding the seed packages by default by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/6

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.0.2...1.1.0

## 1.0.2 (2024-02-16)

### What's Changed

- Use latest version and test other OSs by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/2
- Fix wheel build fails with missing implementation by @gaborbernat in https://github.com/tox-dev/tox-uv/pull/3

### New Contributors

- @gaborbernat made their first contribution in https://github.com/tox-dev/tox-uv/pull/2

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.0.1...1.0.2

## 1.0.1 (2024-02-16)

**Full Changelog**: https://github.com/tox-dev/tox-uv/compare/1.0.0...1.0.1

## 1.0.0 (2024-02-16)

**Full Changelog**: https://github.com/tox-dev/tox-uv/commits/1.0.0
