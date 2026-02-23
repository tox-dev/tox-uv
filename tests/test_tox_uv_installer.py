from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


def test_uv_install_in_ci_list(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    project = tox_project({"tox.ini": "[testenv]\ndeps = tomli\npackage=skip"})
    result = project.run()
    result.assert_success()
    report = {i.split("=")[0] for i in result.out.splitlines()[-3][4:].split(",")}
    assert report == {"tomli"}


def test_uv_install_in_ci_seed(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\nuv_seed = true"})
    result = project.run()
    result.assert_success()
    report = {i.split("=")[0] for i in result.out.splitlines()[-3][4:].split(",")}
    if sys.version_info >= (3, 12):  # pragma: >=3.12 cover
        assert report == {"pip"}
    else:  # pragma: <3.12 cover
        assert report == {"pip", "setuptools", "wheel", "packaging"}


def test_uv_install_with_pre(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\ndeps = tomli\npip_pre = true\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


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
    result = project.run("-vv")
    result.assert_success()


def test_uv_install_without_pre_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli
    package = skip
    install_command = uv pip install {packages}
    """
    })
    result = project.run("-vv")
    result.assert_success()


@pytest.mark.parametrize("strategy", ["highest", "lowest", "lowest-direct"])
def test_uv_install_with_resolution_strategy(tox_project: ToxProjectCreator, strategy: str) -> None:
    project = tox_project({"tox.ini": f"[testenv]\ndeps = tomli>=2.0.1\npackage = skip\nuv_resolution = {strategy}"})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

    result = project.run("-vv")
    result.assert_success()

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
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

    result = project.run("-vv")
    result.assert_success()

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
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("-vv")
    result.assert_success()
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
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

    result = project.run("-vv")
    result.assert_success()

    install_calls = [call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert len(install_calls) == 1
    cmd = install_calls[0][2:]
    assert cmd[0] == "install"
    assert "--resolution" in cmd
    assert "lowest-direct" in cmd
    assert "packaging>=20.0" in cmd
    assert "pytest>=8.0.0" in cmd


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
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

    result = project.run("-vv")
    result.assert_success()

    install_calls = [call[0][3].cmd for call in execute_calls.call_args_list if "install" in call[0][3].run_id]
    assert len(install_calls) == 1
    cmd = install_calls[0][2:]
    assert cmd[0] == "install"
    assert "--resolution" in cmd
    assert "lowest-direct" in cmd
    assert "tomli>=2.0.0" in cmd
    assert "pytest>=8.0.0" in cmd


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
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

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


def test_uv_install_broken_venv(tox_project: ToxProjectCreator) -> None:
    """Tests ability to detect that a venv a with broken symlink to python interpreter is recreated."""
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
    if sys.platform != "win32":  # pragma: win32 no cover
        bin_dir = project.path / ".tox" / "py" / "bin"
        executables = ("python", "python3")
    else:  # pragma: win32 cover
        bin_dir = project.path / ".tox" / "py" / "Scripts"
        executables = ("python.exe", "pythonw.exe")
    bin_dir.mkdir(parents=True, exist_ok=True)
    for filename in executables:
        path = bin_dir / filename
        path.unlink(missing_ok=True)
        path.symlink_to("/broken-location")
    # run again and ensure we did run the repair bits
    result = project.run("run", "-v")
    result.assert_success()
    assert "recreate env because existing venv is broken" in result.out
