from __future__ import annotations

import json
import platform
import sys
import sysconfig
from platform import python_implementation

print(  # ruff:ignore[print]
    json.dumps({
        "implementation": python_implementation().lower(),
        "version_info": sys.version_info,
        "version": sys.version,
        "is_64": sys.maxsize > 2**32,
        "libc": platform.libc_ver(),
        "free_threaded": bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
    })
)
