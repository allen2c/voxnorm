# Experiments

The lab notebook: every probe, review, measurement, or survey whose result
changed (or deliberately did not change) what voxnorm does. Code and the
module docstrings say *what* the package does; this directory keeps *how we
found out*, so a later contributor can re-run the evidence instead of
re-arguing it.

## Layout

One directory per experiment, numbered in the order it was run:

```
docs/experiments/
  README.md                       this index
  TEMPLATE.md                     copy it to start an experiment
  0001-customer-service-phone-forms/
    README.md                     the record
  0002-multi-angle-review-of-0.2.1/
    README.md                     the record
    probe.py                      re-runnable evidence
    results-v0.2.1.txt            its output, frozen at that version
```

- **Name**: `NNNN-what-was-asked`, words spelled out. Cite the whole name,
  never the number alone (`0002-multi-angle-review-of-0.2.1`).
- **`README.md`** is the record and follows [TEMPLATE.md](TEMPLATE.md):
  question, setup, method, findings, decision.
- **`probe.py`** (optional) reproduces the findings from a clean checkout
  with `uv run python docs/experiments/<name>/probe.py`. No machine paths,
  no network, no files written outside the experiment directory. A probe
  that tracks planned fixes tags each case with its target release and
  prints `pending` until that release, so one table can follow a feature to
  completion.
- **`results-vX.Y.Z.txt`** freezes a probe's output at the version it ran
  against. Add a new file per version; never edit an old one.
- **Findings** get a kebab-case slug that says what is wrong
  (`percent-quadratic-backtracking`), unique within the experiment.
  [docs/roadmap.md](../roadmap.md) and commit messages cite
  `<experiment name>/<finding slug>`.

## Rules

- A record is written when the experiment runs, then frozen. A later
  experiment that overturns it says so and links back; the old record gets
  one line under **Status** (`superseded by 0007-…`), nothing else.
- Keep raw dumps out. Commit the probe and the frozen output; summarise in
  the record. Long transcripts, caches, and local paths stay local.
- Test data copied from other projects is de-identified first
  ([testing.md](../testing.md)).
- A finding that becomes a code change lands with a unit test in `tests/`.
  The probe is evidence, not the test suite.

## Index

| Experiment | Date | Against | Question | Status |
| --- | --- | --- | --- | --- |
| [0001-customer-service-phone-forms](0001-customer-service-phone-forms/README.md) | 2026-10-21 | 0.2.0 | Why do zh-TW customer-service phone numbers, IDs and serials read wrong? | decided, shipped in 0.2.1 |
| [0002-multi-angle-review-of-0.2.1](0002-multi-angle-review-of-0.2.1/README.md) | 2026-10-21 | 0.2.1 | What is still wrong, from four independent angles? | decided; 0.2.2 and 0.3.0 items shipped |
| [0003-finance-technology-real-estate-spoken-forms](0003-finance-technology-real-estate-spoken-forms/README.md) | 2026-10-30 | 0.5.1 | What do finance, technology and real-estate calls and podcasts write that voxnorm misreads? | decided, 0.6.0 |
