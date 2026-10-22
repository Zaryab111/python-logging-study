# Results

2069 non-test files, 447382 lines of code, 3227 exception handlers in 21 projects (libraries: 15, applications: 6).

## RQ1: how common is logging, by project type?

- applications: 2.24 logging calls per 1000 lines (project medians 2.91).
- libraries: 0.28 logging calls per 1000 lines (project medians 0.00).
- Mann-Whitney U test between applications and libraries (projects as units): p = 0.00236.

## RQ2: which levels are used?

- debug: 164 calls (22.7%)
- info: 205 calls (28.4%)
- warning: 139 calls (19.2%)
- error: 114 calls (15.8%)
- exception: 76 calls (10.5%)
- critical: 25 calls (3.5%)

## RQ3: do exception handlers log, and what else do they do?

- applications: 11.2% log, 28.4% re-raise, 19.5% only `pass`/`continue`.
- libraries: 0.3% log, 31.4% re-raise, 15.9% only `pass`/`continue`.

## Per project

| group | project | logging calls / 1000 lines | handlers | handlers that log | handlers that swallow |
|---|---|---|---|---|---|
| applications | black | 0.26 | 94 | 1.1% | 19.1% |
| applications | textual | 0.45 | 434 | 3.5% | 26.0% |
| applications | alembic | 2.08 | 55 | 0.0% | 14.5% |
| applications | mitmproxy | 3.74 | 361 | 13.6% | 8.6% |
| applications | celery | 4.47 | 672 | 10.9% | 21.6% |
| applications | gunicorn | 9.77 | 486 | 20.0% | 19.5% |
| libraries | attrs | 0.00 | 21 | 0.0% | 14.3% |
| libraries | click | 0.00 | 83 | 0.0% | 19.3% |
| libraries | itsdangerous | 0.00 | 15 | 0.0% | 6.7% |
| libraries | loguru | 0.00 | 50 | 0.0% | 18.0% |
| libraries | marshmallow | 0.00 | 51 | 0.0% | 11.8% |
| libraries | pluggy | 0.00 | 24 | 0.0% | 8.3% |
| libraries | requests | 0.00 | 66 | 0.0% | 9.1% |
| libraries | starlette | 0.00 | 64 | 0.0% | 17.2% |
| libraries | werkzeug | 0.00 | 177 | 0.0% | 20.9% |
| libraries | jinja | 0.18 | 101 | 1.0% | 19.8% |
| libraries | boltons | 0.22 | 201 | 0.0% | 13.9% |
| libraries | httpx | 0.28 | 55 | 0.0% | 7.3% |
| libraries | flask | 0.41 | 43 | 2.3% | 9.3% |
| libraries | rich | 0.47 | 82 | 1.2% | 12.2% |
| libraries | tqdm | 2.67 | 92 | 0.0% | 23.9% |

## Threats to validity

- Logging calls are recognised by the receiver name (logger, log, logging, ...). Other names and `print` are missed.
- The two groups are small, hand-picked samples (not random), so the comparison is indicative, not general.
- Only the latest snapshot of each project is analysed, not history. Applications were cloned shallowly (latest commit only).
- Test files are excluded by path rules, which may misclassify some files.
- A handler that re-raises or calls a helper that logs is not counted as logging.