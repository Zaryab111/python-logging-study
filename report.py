"""Turn data/files_*.csv and data/handlers_*.csv into results.md and figures."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

ROOT = Path(__file__).parent
files = pd.concat([pd.read_csv(p) for p in sorted((ROOT / "data").glob("files_*.csv"))], ignore_index=True)
hand = pd.concat([pd.read_csv(p) for p in sorted((ROOT / "data").glob("handlers_*.csv"))], ignore_index=True)
(ROOT / "figures").mkdir(exist_ok=True)

lvl_cols = ["debug", "info", "warning", "error", "exception", "critical"]
files["log_calls"] = files[lvl_cols].sum(axis=1)

per_repo = files.groupby(["group", "repo"]).agg(loc=("loc", "sum"), log_calls=("log_calls", "sum"))
per_repo["logs_per_kloc"] = per_repo.log_calls / per_repo["loc"] * 1000
h = hand.groupby(["group", "repo"]).agg(handlers=("logs", "count"), logging=("logs", "mean"),
                                         reraising=("raises", "mean"), swallowing=("swallows", "mean"))
res = per_repo.join(h).fillna(0).reset_index()

out = ["# Results\n"]
out.append(f"{len(files)} non-test files, {int(files['loc'].sum())} lines of code, {len(hand)} exception handlers "
           f"in {len(res)} projects ({', '.join(f'{g}: {n}' for g, n in res.group.value_counts().items())}).\n")

out.append("## RQ1: how common is logging, by project type?\n")
for g, d in res.groupby("group"):
    tot = d.log_calls.sum() / d["loc"].sum() * 1000
    out.append(f"- {g}: {tot:.2f} logging calls per 1000 lines (project medians {d.logs_per_kloc.median():.2f}).")
groups = list(res.group.unique())
if len(groups) == 2:
    a, b = (res[res.group == g].logs_per_kloc for g in groups)
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    out.append(f"- Mann-Whitney U test between {groups[0]} and {groups[1]} (projects as units): p = {p:.3g}.")
out.append("")

out.append("## RQ2: which levels are used?\n")
tot = files[lvl_cols].sum()
for c in lvl_cols:
    out.append(f"- {c}: {int(tot[c])} calls ({tot[c] / tot.sum():.1%})")
out.append("")

out.append("## RQ3: do exception handlers log, and what else do they do?\n")
for g, d in hand.groupby("group"):
    out.append(f"- {g}: {d.logs.mean():.1%} log, {d.raises.mean():.1%} re-raise, {d.swallows.mean():.1%} only `pass`/`continue`.")
out.append("")

out.append("## Per project\n")
out.append("| group | project | logging calls / 1000 lines | handlers | handlers that log | handlers that swallow |")
out.append("|---|---|---|---|---|---|")
for _, r in res.sort_values(["group", "logs_per_kloc"]).iterrows():
    out.append(f"| {r.group} | {r.repo} | {r.logs_per_kloc:.2f} | {int(r.handlers)} | {r.logging:.1%} | {r.swallowing:.1%} |")
out.append("")

out.append("## Threats to validity\n")
out.append("- Logging calls are recognised by the receiver name (logger, log, logging, ...). Other names and `print` are missed.")
out.append("- The two groups are small, hand-picked samples (not random), so the comparison is indicative, not general.")
out.append("- Only the latest snapshot of each project is analysed, not history. Applications were cloned shallowly (latest commit only).")
out.append("- Test files are excluded by path rules, which may misclassify some files.")
out.append("- A handler that re-raises or calls a helper that logs is not counted as logging.")
(ROOT / "results.md").write_text("\n".join(out), encoding="utf-8")

fig, ax = plt.subplots(figsize=(8, 6))
colors = {g: c for g, c in zip(groups, ["#1f4e8c", "#c0504d", "#4f9a5a"])}
d = res.sort_values("logs_per_kloc")
ax.barh(d.repo, d.logs_per_kloc, color=[colors[g] for g in d.group])
ax.set_xlabel("logging calls per 1000 lines of code")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=colors[g]) for g in groups], labels=groups)
plt.tight_layout()
plt.savefig(ROOT / "figures" / "logging_density.png", dpi=150)
plt.close()
print("\n".join(out))
