# Releasing

Releases are tags; CI does the rest.

1. Bump the version in `pyproject.toml` and `voxnorm/__init__.py`
   (`__version__`) — they must agree.
2. Add a `CHANGELOG.md` section for the version.
3. Commit, then tag and push:

   ```sh
   git tag vX.Y.Z
   git push origin main --tags
   ```

4. `.github/workflows/release.yml` builds sdist + wheel with `uv build` and
   publishes to PyPI via **trusted publishing** — no token lives anywhere.
   The publisher is configured once on pypi.org (project `voxnorm`, owner
   `allen2c`, repo `voxnorm`, workflow `release.yml`, environment `pypi`).

`ci.yml` runs ruff + pytest on 3.10 and 3.13 for every push and PR; a tag
should never be cut from a red main.
