Preserve debug and free-threaded flags when selecting Python for a tox environment. Changing either flag recreates the
environment, so `py313d` and `py313td` do not reuse an interpreter with different build options.
