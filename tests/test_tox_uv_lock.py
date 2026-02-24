from __future__ import annotations

import shutil
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_with_setupdir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """\
[testenv]
runner = uv-venv-lock-runner
package_root = src
""",
    })
    (project.path / "src").mkdir()
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("run", "--notest", "-vv")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--directory",
                str(project.path / "src"),
                "--locked",
                "--python-preference",
                "system",
                "-v",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_list_dependencies_command(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    extras =
        type
        dev
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("--list-dependencies", "-vv")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--extra",
                "dev",
                "--extra",
                "type",
                "-v",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "freeze", [uv, "--color", "never", "pip", "freeze"]),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert len(calls) == len(expected)
    for i in range(len(calls)):
        assert calls[i] == expected[i]


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize("verbose", ["", "-v", "-vv", "-vvv"])
def test_uv_lock_command(tox_project: ToxProjectCreator, verbose: str) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    extras =
        type
        dev
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run(*[verbose] if verbose else [])
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    v_args = ["-v"] if verbose not in {"", "-v"} else []
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                *v_args,
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--extra",
                "dev",
                "--extra",
                "type",
                *v_args,
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected
    show_uv_output = execute_calls.call_args_list[1].args[4]
    assert show_uv_output is (bool(verbose))


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_with_default_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    no_default_groups = False
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("-vv")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        ("py", "uv-sync", [uv, "sync", "--locked", "--python-preference", "system", "-v", "-p", sys.executable]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    "name",
    [
        "tox_uv-1.12.2-py3-none-any.whl",
        "tox_uv-1.12.2.tar.gz",
    ],
)
def test_uv_lock_with_install_pkg(tox_project: ToxProjectCreator, name: str) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    wheel = project.path / name
    wheel.write_text("")
    result = project.run("-vv", "run", "--installpkg", str(wheel))
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-install-project",
                "-v",
                "-p",
                sys.executable,
            ],
        ),
        (
            "py",
            "install_external",
            [uv, "pip", "install", "--reinstall", "--no-deps", f"tox-uv@{wheel}", "-v"],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize("uv_sync_locked", [True, False])
def test_uv_sync_extra_flags(tox_project: ToxProjectCreator, uv_sync_locked: bool) -> None:
    uv_sync_locked_str = str(uv_sync_locked).lower()
    project = tox_project({
        "tox.ini": f"""
    [testenv]
    runner = uv-venv-lock-runner
    no_default_groups = false
    uv_sync_flags = --no-editable, --inexact
    uv_sync_locked = {uv_sync_locked_str}
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                *(["--locked"] if uv_sync_locked else []),
                "--python-preference",
                "system",
                "--no-editable",
                "--inexact",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_sync_extra_flags_toml(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    no_default_groups = false
    uv_sync_flags = ["--no-editable", "--inexact"]
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-editable",
                "--inexact",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_sync_dependency_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    with_dev = true
    dependency_groups = ["test", "type"]
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-default-groups",
                "--group",
                "test",
                "--group",
                "type",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.parametrize(
    ("uv_python_preference", "injected"),
    [
        pytest.param("none", [], id="on"),
        pytest.param("system", ["--python-preference", "system"], id="off"),
    ],
)
def test_uv_sync_uv_python_preference(
    tox_project: ToxProjectCreator, uv_python_preference: str, injected: list[str]
) -> None:
    project = tox_project({
        "tox.toml": f"""
    [env_run_base]
    runner = "uv-venv-lock-runner"
    with_dev = true
    dependency_groups = ["test", "type"]
    commands = [["python", "hello"]]
    uv_python_preference = "{uv_python_preference}"
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                *injected,
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                *injected,
                "--no-default-groups",
                "--group",
                "test",
                "--group",
                "type",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


def test_skip_uv_sync(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("run", "--skip-uv-sync")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.parametrize("package", ["wheel", "uv"])
def test_uv_package_non_editable(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch, package: str) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": f"""
            [env_run_base]
            runner = "uv-venv-lock-runner"
            package = "{package}"
            """,
        "pyproject.toml": """
            [project]
            name = "demo"
            """,
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("run", "--notest")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-editable",
                "--reinstall-package",
                "demo",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.parametrize("package", ["wheel", "uv"])
def test_uv_package_non_editable_no_pyproject(
    tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch, package: str
) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": f"""
            [env_run_base]
            runner = "uv-venv-lock-runner"
            package = "{package}"
            """,
    })
    project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)

    result = project.run("run", "--notest")

    result.assert_failed()


def test_uv_package_uv_editable(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": """
            [env_run_base]
            runner = "uv-venv-lock-runner"
            package = "uv-editable"
            """,
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("run", "--notest")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


def test_skip_uv_package_skip(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    package = "skip"
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("run", "--notest")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-install-project",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_ith_resolution(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    uv_resolution = highest
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("run", "--notest")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--resolution",
                "highest",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert len(calls) == len(expected)
    for i in range(len(calls)):
        assert calls[i] == expected[i]


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_sync_only_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """\
[env_run_base]
runner = "uv-venv-lock-runner"
only_groups = ["ci"]
commands = [["python", "hello"]]
"""
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--only-group",
                "ci",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected
