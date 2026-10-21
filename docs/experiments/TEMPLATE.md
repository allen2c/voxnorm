# NNNN-what-was-asked

**Date**: YYYY-MM-DD · **Against**: voxnorm X.Y.Z (commit) · **Status**: open | decided | superseded by NNNN-…

## Question

One or two sentences: what we wanted to know, and who asked (a bug report,
a review, a design question).

## Setup

What ran and where it is: the probe (`probe.py`), the corpus, the tools and
versions that matter. Enough for a stranger to re-run it.

## Method

How the evidence was gathered and judged: what counts as correct, which
charter rule applies, what was out of scope.

## Findings

| Finding | Input → actual | Expected | Class |
| --- | --- | --- | --- |
| `kebab-case-slug` | `12, 謝謝` → `12, 謝謝` | `十二, 謝謝` | bug / charter violation / reading / new form / nit |

Also list what was checked and found fine, in one line each; it saves the
next person from re-checking it.

## Decision

What changes and where it is planned (roadmap item or release), what does
not change and why (cite the charter), and which questions stay open.
