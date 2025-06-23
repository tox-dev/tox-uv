from __future__ import annotations

import shutil
import sysconfig

# presence of 'uv' package is not required for use of uv as uv can be installed
# as a standalone tool and still work fine. Also if uv is inside a virtualenv
# importing might make its internal uv.find_uv_bin return an exception even if
# we might have a working uv executable.


def find_uv_bin() -> str:
    """Return the uv binary path.

    :raises FileNotFoundError: if uv is not found.
    """

    try:
        import uv  # noqa: PLC0415

        path = uv.find_uv_bin()
    except (ImportError, FileNotFoundError):  # pragma: no cover
        uv_exe = "uv" + sysconfig.get_config_var("EXE")
        path = shutil.which(uv_exe)
        if not path:
            # pylint: disable=raise-missing-from
            raise FileNotFoundError(uv_exe)  # noqa: B904
    return path
