# Contributing

Install the project with `tox run -e dev` and run the tests with `tox run -e 3.15`. Run `prek run --all-files` before
pushing changes.

## Release notes

Add one `changelog.d/+short-name.<category>.md` file for each user-facing change. A pull request can contain several
fragments, including more than one category. Release preparation resolves the pull request number and human authors from
the squash merge; do not put a number or author credit in the fragment text. A numeric fragment name remains supported.

Use `feature` for new behavior and Python support additions or removals, `change` for changes to existing behavior,
`bugfix` for corrections, and `doc` for documentation changes users need to know about. Use `breaking`, `security`,
`performance`, `deprecation`, `removal`, or `packaging` when those describe a user-facing change more precisely. The
tracked changelog calls the first four categories Added, Changes, Fixed, and Documentation. Empty categories are
omitted.

For example, `changelog.d/+workspace-install.bugfix.md` could contain:

```markdown
Install sourced packages from uv workspaces.
```

Apply the `skip news` label to a PR that changes only maintenance work and has no user-facing effect. The news check
runs again if the label changes. Maintenance bot PRs receive the label automatically unless they provide a fragment. Bot
accounts are not listed as authors of release notes.
