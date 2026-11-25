Multiple `base_python` entries are tried in order again: a missing interpreter no longer stops the run when a later
entry is available. The first entry is still used when no entry is available locally, so uv can download a managed
interpreter for it.
