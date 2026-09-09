# Release

1. Move the `Unreleased` section of `CHANGELOG.md` under the new version.
2. Bump `version` in `pyproject.toml` and `__version__` in
   `voxnorm/__init__.py`, then `uv lock` so `uv.lock` follows.
3. `uv run pytest && uv run ruff check .`
4. Commit, tag, push:

   ```sh
   git tag v0.2.0
   git push origin main --tags
   ```

The tag triggers `.github/workflows/release.yml`: `uv build`, then PyPI
trusted publishing from the `pypi` environment. No token lives in the repo;
the publisher is configured once on pypi.org (project `voxnorm`, owner
`allen2c`, workflow `release.yml`, environment `pypi`). Watch the run with
`gh run watch`.
