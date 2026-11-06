With `uv_resolution` and `dependency_groups` both set, `deps` lines are now kept as written when combined with the
groups, so a `-r`/`-c` file, an option or a comment no longer crashes tox with an invalid requirement error.
