# Do exception handlers log? A static study of logging practices in Python projects

A small empirical study of how open-source Python projects use logging, comparing **libraries** with **applications and tools**.

## Research questions
1. How common is logging (calls per 1000 lines), and does it differ between libraries and applications?
2. Which log levels are used?
3. Do exception handlers log, re-raise, or silently swallow the exception?

## Method
- `log_study.py` parses every non-test `.py` file with Python's `ast` module (code is never executed) and counts logging calls by level, lines of code, and the behaviour of every `except` handler.
- Logging calls are recognised by the receiver name (`logger`, `log`, `logging`, ...).
- `report.py` computes per-project rates and compares the groups with a Mann-Whitney U test (projects as units).

## Data
- **Libraries (15):** requests, flask, click, jinja, werkzeug, itsdangerous, httpx, starlette, attrs, tqdm, rich, marshmallow, boltons, pluggy, loguru. Full history clones, analysed at the latest snapshot.
- **Applications and tools (6):** celery, mitmproxy, alembic, gunicorn, textual, black. Shallow clones.
- Both groups are hand-picked, not random.

## Run
```
python log_study.py <folder with libraries> libraries
python log_study.py <folder with applications> applications
python report.py
python -m pytest
```

## Results
See `results.md` and `figures/logging_density.png`. In this sample, applications log about 8 times more than libraries (2.24 vs 0.28 calls per 1000 lines, p = 0.002), and only a small share of exception handlers log in either group.

## Threats to validity
- Receiver-name matching misses logging through other names and does not count `print`. `loguru`, a logging library, shows 0.00 because it is used through its own API, not matched by the name list.
- Small, hand-picked samples: the comparison is indicative, not general.
- Latest snapshot only, not history.
- A handler that calls a helper that logs, or re-raises, is not counted as logging.

## Provenance
The code and the first run were produced by an AI assistant (Claude) as a learning scaffold; the git history records that. Anyone building on it should read the code, extend it, and describe their own contribution here.

## Ideas to extend it (your contribution)
1. Match more logger names by resolving `logging.getLogger` assignments in each file.
2. Add 20 more projects chosen at random from a list, and report the sampling method.
3. Study history: do projects add logging after bug-fix commits?
4. Manually label 100 handlers to measure precision.
