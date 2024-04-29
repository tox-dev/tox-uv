from __future__ import annotations

import json
import sys
from platform import python_implementation

print(  # noqa: T201
    json.dumps({
        "implementation": python_implementation().lower(),
        "version_info": sys.version_info,
        "version": sys.version,
        "is_64": sys.maxsize > 2**32,
    })
)
