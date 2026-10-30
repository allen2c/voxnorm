# Release

A tag goes on `main` only, after the merge and a green CI. Never tag a work
branch, even one that would fast-forward.

1. On the work branch: date the top section of `CHANGELOG.md`, bump `version`
   in `pyproject.toml` and `__version__` in `voxnorm/__init__.py`, and run
   `uv lock`.
2. Audit: every case, test, doc and commit message is de-identified (no real
   emails, domains, names, phone numbers, serials, companies); tests pass on
   CI's Python versions (`uv run --python 3.10 pytest`, then 3.13); `uv build`
   and read the sdist's file list.
3. Merge to `main`, push, and wait for `.github/workflows/ci.yml` (ruff + pytest
   on 3.10 and 3.13). Never cut a tag from a red main.
4. Tag and push:

   ```sh
   git tag v0.6.0
   git push origin v0.6.0
   ```

The tag triggers `.github/workflows/release.yml`: it fails unless the tag equals
`__version__`, runs the tests, `uv build`, then publishes through PyPI trusted
publishing from the `pypi` environment. No token lives in the repo; the
publisher is configured once on pypi.org (project `voxnorm`, owner `allen2c`,
workflow `release.yml`, environment `pypi`).
