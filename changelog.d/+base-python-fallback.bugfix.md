tox-uv now tries each `base_python` entry in order and uses the first one uv finds installed, as tox's virtualenv runner
does; before, it only ever used the first entry. When uv finds none of them, the first entry is used, so uv can still
download a managed interpreter for it.
