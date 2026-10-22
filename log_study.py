"""Do exception handlers log? A static study of logging practices in open-source Python projects.

For each project we parse every .py file with the ast module (no code is executed) and count:
  - logging calls by level (debug, info, warning, error, exception, critical),
  - lines of code,
  - except-handlers, and how many of them contain a logging call, re-raise, or neither.

Usage:  python log_study.py <folder with cloned projects> <group name, e.g. libraries or applications>
Output: data/files_<group>.csv, data/handlers_<group>.csv (then run report.py)
"""
import ast
import csv
import sys
from collections import Counter
from pathlib import Path

LEVELS = {"debug", "info", "warning", "warn", "error", "exception", "critical", "fatal"}
LOGGER_NAMES = {"logging", "logger", "log", "_logger", "_log", "LOGGER", "LOG"}

ROOT = Path(__file__).parent
DATA = ROOT / "data"


def is_log_call(node: ast.AST) -> str | None:
    """Return the level name if this node is something like logger.error(...) or logging.info(...)."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in LEVELS:
            base = node.func.value
            name = base.id if isinstance(base, ast.Name) else (base.attr if isinstance(base, ast.Attribute) else None)
            if name in LOGGER_NAMES:
                return "warning" if node.func.attr == "warn" else ("critical" if node.func.attr == "fatal" else node.func.attr)
    return None


def analyse_file(path: Path):
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    loc = sum(1 for line in src.splitlines() if line.strip() and not line.strip().startswith("#"))
    levels = Counter()
    handlers = []
    for node in ast.walk(tree):
        lvl = is_log_call(node)
        if lvl:
            levels[lvl] += 1
        if isinstance(node, ast.ExceptHandler):
            body_nodes = [n for stmt in node.body for n in ast.walk(stmt)]
            logs = any(is_log_call(n) for n in body_nodes)
            raises = any(isinstance(n, ast.Raise) for n in body_nodes)
            swallow = all(isinstance(s, (ast.Pass, ast.Continue)) for s in node.body)
            handlers.append((logs, raises, swallow))
    return loc, levels, handlers


def is_test_file(p: Path) -> bool:
    s = str(p).lower().replace("\\", "/")
    return "/tests/" in s or "/test/" in s or p.name.startswith("test_") or p.name == "conftest.py"


def main(folder: str, group: str):
    DATA.mkdir(exist_ok=True)
    files_rows, handler_rows = [], []
    for repo_dir in sorted(Path(folder).iterdir()):
        if not repo_dir.is_dir():
            continue
        for p in repo_dir.rglob("*.py"):
            if ".git" in p.parts or "node_modules" in p.parts or is_test_file(p):
                continue
            r = analyse_file(p)
            if r is None:
                continue
            loc, levels, handlers = r
            files_rows.append([group, repo_dir.name, str(p.relative_to(repo_dir)), loc] + [levels.get(l, 0) for l in
                              ("debug", "info", "warning", "error", "exception", "critical")])
            for logs, raises, swallow in handlers:
                handler_rows.append([group, repo_dir.name, str(p.relative_to(repo_dir)), int(logs), int(raises), int(swallow)])
        print("done", repo_dir.name)

    with open(DATA / f"files_{group}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group", "repo", "file", "loc", "debug", "info", "warning", "error", "exception", "critical"])
        w.writerows(files_rows)
    with open(DATA / f"handlers_{group}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group", "repo", "file", "logs", "raises", "swallows"])
        w.writerows(handler_rows)
    print(f"{len(files_rows)} files, {len(handler_rows)} handlers")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

