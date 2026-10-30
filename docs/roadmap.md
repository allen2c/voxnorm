# Roadmap

What is planned, why, and how each item is checked. Items cite their evidence
as `<experiment>/<finding>` ([experiments/](experiments/README.md)); the
probe of that experiment is the acceptance table, and every item also lands
with unit tests in `tests/`. An item is done when its probe cases pass and
`uv run pytest`, `ruff check`, `ruff format --check` are green.

## Shipped

| Release | Scope | Plan |
| --- | --- | --- |
| v0.2.2 | Correctness, no new forms | [roadmap/v0.2.2.md](roadmap/v0.2.2.md) |
| v0.3.0 | New structural forms | [roadmap/v0.3.0.md](roadmap/v0.3.0.md) |
| v0.6.0 | Finance, technology and real-estate forms | [0003 record](experiments/0003-finance-technology-real-estate-spoken-forms/README.md) |

## Next

Nothing is planned. Real ja, ko or zh-CN call or podcast text would test the
0.6.0 readings; re-run the 0003 probe when any arrives.

## Deferred, no work planned (status quo stays)

`ko-native-counters` and `ko-room-reading` (until there is a Korean use case);
`year-as-duration` and `room-shi-as-count` (known residuals, see 0002); en
US/UK "and", zh-CN `$` as 美元, and group pauses in zh/ja phone readings (no
caller has asked). 0.6.0 left `3Q25` and `1H26` as letter-glued digits and
clocks in 24-hour readings by decision (see 0003).
