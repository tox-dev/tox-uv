from __future__ import annotations

import sys
from textwrap import dedent
from typing import TYPE_CHECKING, Final, TypeVar
from zipfile import ZipFile

import pytest
from tox.config.sets import CoreConfigSet

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture
    from tox.execute.request import ExecuteRequest
    from tox.pytest import ToxProjectCreator

_CI_SEED_PACKAGES: Final[set[str]] = (
    {"pip"} if sys.version_info >= (3, 12) else {"pip", "setuptools", "wheel", "packaging"}
)
_BROKEN_VENV_BIN: Final[str] = "bin" if sys.platform != "win32" else "Scripts"
_BROKEN_VENV_EXECUTABLES: Final[tuple[str, ...]] = (
    ("python", "python3") if sys.platform != "win32" else ("python.exe", "pythonw.exe")
)


def test_uv_install_in_ci_list(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    result = tox_project({"tox.ini": "[testenv]\ndeps = tomli\npackage=skip"}).run()
    result.assert_success()
    report = {i.split("=")[0] for i in result.out.splitlines()[-3][4:].split(",")}
    assert report == {"tomli"}


def test_uv_install_in_ci_seed(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    result = tox_project({"tox.ini": "[testenv]\npackage=skip\nuv_seed = true"}).run()
    result.assert_success()
    report = {i.split("=")[0] for i in result.out.splitlines()[-3][4:].split(",")}
    assert report == _CI_SEED_PACKAGES


def test_uv_install_with_pre(tox_project: ToxProjectCreator) -> None:
    tox_project({"tox.ini": "[testenv]\ndeps = tomli\npip_pre = true\npackage=skip"}).run("-vv").assert_success()


def test_uv_install_with_pre_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli
    pip_pre = true
    package = skip
    install_command = uv pip install {packages}
    """
    })
    project.run("-vv").assert_success()


def test_uv_install_without_pre_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli
    package = skip
    install_command = uv pip install {packages}
    """
    })
    project.run("-vv").assert_success()


@pytest.mark.parametrize(
    "strategy",
    [
        pytest.param("highest", id="highest"),
        pytest.param("lowest", id="lowest"),
        pytest.param("lowest-direct", id="lowest-direct"),
    ],
)
def test_uv_install_with_resolution_strategy(tox_project: ToxProjectCreator, strategy: str) -> None:
    project = tox_project({"tox.ini": f"[testenv]\ndeps = tomli>=2.0.1\npackage = skip\nuv_resolution = {strategy}"})
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    assert execute_calls.call_args[0][3].cmd[2:] == ["install", "--resolution", strategy, "tomli>=2.0.1", "-v"]


def test_uv_install_with_invalid_resolution_strategy(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\ndeps = tomli>=2.0.1\npackage = skip\nuv_resolution = invalid"})

    result = project.run("-vv")
    result.assert_failed(code=1)

    assert "Invalid value for uv_resolution: 'invalid'." in result.out


def test_uv_install_with_resolution_strategy_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli>=2.0.1
    package = skip
    uv_resolution = lowest-direct
    install_command = uv pip install {packages}
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    assert execute_calls.call_args[0][3].cmd[2:] == ["install", "tomli>=2.0.1", "--resolution", "lowest-direct"]


def test_uv_install_with_resolution_strategy_and_pip_pre(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli>=2.0.1
    package = skip
    uv_resolution = lowest-direct
    pip_pre = true
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)
    project.run("-vv").assert_success()
    assert execute_calls.call_args[0][3].cmd[2:] == [
        "install",
        "--prerelease",
        "allow",
        "--resolution",
        "lowest-direct",
        "tomli>=2.0.1",
        "-v",
    ]


def test_uv_install_with_resolution_strategy_and_dependency_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
[testenv]
deps = packaging>=20.0
package = skip
uv_resolution = lowest-direct
dependency_groups = test
""",
        "pyproject.toml": """
[project]
name = "test-pkg"
version = "0.1.0"

[dependency-groups]
test = ["pytest>=8.0.0"]
""",
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    install_calls = [call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert len(install_calls) == 1
    cmd = install_calls[0][2:]
    assert cmd[0] == "install"
    assert "--resolution" in cmd
    assert "lowest-direct" in cmd
    assert "packaging>=20.0" in cmd
    assert "pytest>=8.0.0" in cmd


def test_uv_install_dependency_groups_without_package_root(
    tox_project: ToxProjectCreator, mocker: MockerFixture
) -> None:
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\nuv_resolution=lowest-direct\ndependency_groups=test",
        "pyproject.toml": '[dependency-groups]\ntest = ["pytest>=8"]',
    })
    original_get = CoreConfigSet.get
    config_value = TypeVar("config_value")

    def get_without_package_root(core: CoreConfigSet, item: str, of_type: type[config_value]) -> config_value:
        if item == "package_root":
            raise KeyError(item)
        return original_get(core, item, of_type)

    mocker.patch.object(CoreConfigSet, "get", autospec=True, side_effect=get_without_package_root)
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    assert next(call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id)[2:] == [
        "install",
        "--resolution",
        "lowest-direct",
        "pytest>=8",
        "-v",
    ]


def test_uv_install_lowest_direct_with_dependency_groups_and_package(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
[testenv]
deps = tomli>=2.0.0
uv_resolution = lowest-direct
dependency_groups = test
package = skip
""",
        "pyproject.toml": """
[project]
name = "test-pkg"
version = "0.1.0"
dependencies = ["packaging>=20.0"]

[dependency-groups]
test = ["pytest>=8.0.0"]
""",
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    install_calls = [call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert len(install_calls) == 1
    cmd = install_calls[0][2:]
    assert cmd[0] == "install"
    assert "--resolution" in cmd
    assert "lowest-direct" in cmd
    assert "tomli>=2.0.0" in cmd
    assert "pytest>=8.0.0" in cmd


@pytest.mark.parametrize(
    ("deps", "expected"),
    [
        pytest.param(
            "# pinned for the lowest run\n    -r requirements.txt",
            ["pytest>=8.0.0", "-r", "requirements.txt"],
            id="requirements",
        ),
        pytest.param(
            "-c requirements.txt\n    packaging",
            ["packaging", "pytest>=8.0.0", "-c", "requirements.txt"],
            id="constraints",
        ),
        pytest.param("--no-deps\n    packaging", ["packaging", "pytest>=8.0.0", "--no-deps"], id="option"),
    ],
)
def test_uv_install_resolution_dependency_groups_with_deps_options(
    tox_project: ToxProjectCreator, deps: str, expected: list[str]
) -> None:
    project = tox_project({
        "tox.ini": f"""
[testenv]
deps =
    {deps}
package = skip
uv_resolution = lowest-direct
dependency_groups = test
""",
        "requirements.txt": "packaging>=20.0\n",
        "pyproject.toml": """
[project]
name = "test-pkg"
version = "0.1.0"

[dependency-groups]
test = ["pytest>=8.0.0"]
""",
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    assert [call[0][3].cmd[2:] for call in execute_calls.call_args_list if "install" in call[0][3].run_id] == [
        [
            "install",
            "--resolution",
            "lowest-direct",
            *expected,
            "-v",
        ]
    ]


def test_uv_install_resolution_groups_preserves_set_env(tox_project: ToxProjectCreator) -> None:
    pytest.importorskip("tox", minversion="4.67.5", reason="tox 4.67.5 added set_env expansion in requirements files")
    project = tox_project({
        "tox.ini": """
[testenv]
deps = -r requirements.txt
set_env = GROUP_DEP = packaging>=20.0
package = skip
uv_resolution = lowest-direct
dependency_groups = test
""",
        "requirements.txt": "${GROUP_DEP}\n",
        "pyproject.toml": '[dependency-groups]\ntest = ["pytest>=8.0.0"]',
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()
    execute_calls.reset_mock()
    project.run("-vv", "-x", "testenv.set_env=GROUP_DEP=packaging>=21.0").assert_success()

    assert [call[0][3].cmd[2:] for call in execute_calls.call_args_list if "install" in call[0][3].run_id] == [
        ["install", "--resolution", "lowest-direct", "pytest>=8.0.0", "-r", "requirements.txt", "-v"]
    ]


def test_uv_install_resolution_groups_upgrade_cache(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\ndeps=packaging>=20\nuv_resolution=lowest-direct\ndependency_groups=test",
        "pyproject.toml": '[dependency-groups]\ntest=["pytest>=8"]',
    })
    project.patch_execute(lambda request: 0 if "install" in request.run_id else None)
    result = project.run("-vv")
    result.assert_success()

    # Earlier releases stored combined dependencies using the list installer's cache format.
    cache = result.state.envs["py"].cache
    with (
        cache.compare({"deps": {"req": ["packaging>=20", "pytest>=8"], "env": {}, "constraints": []}}, "PythonRun"),
        cache.compare(None, "UvVenvRunner"),
    ):
        pass
    obsolete_package = project.path / ".tox" / "py" / "obsolete-package"
    obsolete_package.write_text("removed dependency")
    project.run("-vv").assert_success()

    assert not obsolete_package.exists()


@pytest.mark.parametrize(
    ("initial_groups", "other_groups", "expected"),
    [
        pytest.param("", "test", ["packaging==20.0"], id="enable-groups"),
        pytest.param("test", "", ["packaging==20.0", "pytest>=8"], id="disable-groups"),
    ],
)
def test_uv_install_resolution_groups_switch_cache(
    tox_project: ToxProjectCreator, initial_groups: str, other_groups: str, expected: list[str]
) -> None:
    project = tox_project({
        "tox.ini": f"""
[testenv]
package = skip
deps = packaging==20.0
uv_resolution = lowest-direct
dependency_groups = {initial_groups}
""",
        "pyproject.toml": '[dependency-groups]\ntest=["pytest>=8"]',
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)
    project.run("-vv").assert_success()
    project.run(
        "-vv", "-x", "testenv.deps=packaging==21.0", "-x", f"testenv.dependency_groups={other_groups}"
    ).assert_success()
    execute_calls.reset_mock()
    project.run("-vv").assert_success()

    assert [call[0][3].cmd[2:] for call in execute_calls.call_args_list if "install" in call[0][3].run_id] == [
        ["install", "--resolution", "lowest-direct", *expected, "-v"]
    ]


def test_uv_install_with_skip_env_install(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
[testenv]
deps = packaging>=20.0
package = skip
uv_resolution = lowest-direct
dependency_groups = test
""",
        "pyproject.toml": """
[project]
name = "test-pkg"
version = "0.1.0"

[dependency-groups]
test = ["pytest>=8.0.0"]
""",
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    result = project.run("-vv", "--skip-env-install")
    result.assert_success()

    install_calls = [call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert len(install_calls) == 0
    assert "skip installing dependencies and package" in result.out


def test_uv_install_with_pylock(tox_project: ToxProjectCreator) -> None:
    pylock_content = """
version = 1

[[package]]
name = "tomli"
version = "2.0.1"
"""
    project = tox_project({
        "tox.ini": """
[testenv]
package = skip
pylock = pylock.toml
""",
        "pyproject.toml": """
[project]
name = "test-pkg"
version = "0.1.0"
""",
        "pylock.toml": pylock_content,
    })

    result = project.run("-vv")
    result.assert_failed()
    assert "uv cannot install" in result.out


@pytest.mark.parametrize(
    ("initial_setenv", "changed_setenv", "expected_installs"),
    [
        pytest.param("", "UV_EXCLUDE_NEWER = 2024-01-01", 1, id="resolution_env_var_change"),
        pytest.param(
            "setenv = UV_CONCURRENT_DOWNLOADS = 4", "UV_CONCURRENT_DOWNLOADS = 8", 0, id="non_resolution_env_var_change"
        ),
    ],
)
def test_uv_env_var_change_reinstall(
    tox_project: ToxProjectCreator,
    initial_setenv: str,
    changed_setenv: str,
    expected_installs: int,
) -> None:
    project = tox_project({
        "tox.ini": dedent(f"""
            [testenv]
            deps = tomli
            package = skip
            {initial_setenv}
        """),
    })
    install_count = 0

    def handle(request: ExecuteRequest) -> int | None:
        nonlocal install_count
        if "install" in request.run_id:
            install_count += 1
            return 0
        return None

    project.patch_execute(handle)

    result = project.run("r")
    result.assert_success()
    assert install_count == 1
    install_count = 0

    (project.path / "tox.ini").write_text(
        dedent(f"""
        [testenv]
        deps = tomli
        package = skip
        setenv = {changed_setenv}
    """)
    )
    result = project.run("r")
    result.assert_success()
    assert install_count == expected_installs


def test_uv_install_broken_venv(tox_project: ToxProjectCreator) -> None:
    # Tests ability to detect that a venv a with broken symlink to python interpreter is recreated.
    project = tox_project({
        "tox.ini": """
    [testenv]
    skip_install = true
    install = false
    commands = {env_python} --version
    """
    })
    result = project.run("run", "-v")
    result.assert_success()
    assert "recreate env because existing venv is broken" not in result.out
    # break the environment
    bin_dir = project.path / ".tox" / "py" / _BROKEN_VENV_BIN
    executables = _BROKEN_VENV_EXECUTABLES
    bin_dir.mkdir(parents=True, exist_ok=True)
    for filename in executables:
        path = bin_dir / filename
        path.unlink(missing_ok=True)
        path.symlink_to("/broken-location")
    # run again and ensure we did run the repair bits
    result = project.run("run", "-v")
    result.assert_success()
    assert "recreate env because existing venv is broken" in result.out


def test_uv_install_with_constraints_for_deps(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": dedent("""
            [testenv]
            package = skip
            dependency_groups = test
            constraints = constraints.txt
        """),
        "pyproject.toml": dedent("""
            [project]
            name = "test-pkg"
            version = "0.1.0"

            [dependency-groups]
            test = ["pytest>=8.0.0"]
        """),
        "constraints.txt": "pytest==8.3.0\n",
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("-vv").assert_success()

    install_calls = [call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert len(install_calls) == 1
    cmd = install_calls[0][2:]  # skip uv binary and "pip"
    assert cmd[0] == "install"
    assert "pytest>=8.0.0" in cmd
    assert "-c" in cmd


@pytest.mark.parametrize(
    ("source", "dependency"),
    [
        pytest.param("demo-foo", "Demo_Foo", id="dependency-spelling"),
        pytest.param("Demo.Foo", "demo-foo", id="source-spelling"),
    ],
)
def test_uv_install_workspace_source_any_spelling(
    tox_project: ToxProjectCreator, tmp_path: Path, source: str, dependency: str
) -> None:
    wheel = tmp_path / "demo_root-0.1.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as zip_file:
        metadata = f"Metadata-Version: 2.1\nName: demo-root\nVersion: 0.1.0\nRequires-Dist: {dependency}\n"
        zip_file.writestr("demo_root-0.1.0.dist-info/METADATA", metadata)
    project = tox_project({
        "tox.ini": "[testenv]\n",
        "pyproject.toml": dedent(f"""
            [project]
            name = "demo-root"
            version = "0.1.0"
            dependencies = ["{dependency}"]

            [tool.uv]
            sources."{source}" = {{ workspace = true }}
        """),
    })
    execute_calls = project.patch_execute(lambda request: 0 if "install" in request.run_id else None)

    project.run("r", "--installpkg", str(wheel)).assert_success()

    install_calls = [call[0][3].cmd[2:] for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert install_calls[0] == ["install", "--reinstall", "-e", "."]
    assert not any(dependency in cmd for cmd in install_calls)
