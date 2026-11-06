A package dependency that names a uv workspace member is now matched against `tool.uv.sources` by its normalized name,
so `Demo_Foo` and `demo-foo` count as the same member instead of being sent to the index.
