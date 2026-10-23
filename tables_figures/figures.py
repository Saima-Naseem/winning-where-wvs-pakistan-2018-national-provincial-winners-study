"""
Core figures for the paper, drawn from results/results.json (values read from the
stage logs; nothing typed by hand). Output: figures/Figure1..4 as 300-dpi PNG.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
F = ROOT / "figures"; F.mkdir(exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 9.5,
                     "axes.edgecolor": "#8a8a85", "axes.linewidth": 0.6,
                     "xtick.color": "#4a4a46", "ytick.color": "#2b2b28",
                     "savefig.dpi": 300, "savefig.bbox": "tight"})
C = ["#2a78d6", "#eb6834", "#1baf7a"]          # validated categorical slots 1-3
MK = ["o", "s", "^"]                            # shape = secondary encoding (print / colour-blind)
GRID, ZERO = "#e6e6e3", "#6f6f6a"
rows = lambda key: dict(R[key])

OUTCOMES = ["scale_process", "scale_malprac", "conf_elections", "democracy_rating", "satisfaction"]
OUT_LAB = {"scale_process": "Process fairness", "scale_malprac": "Malpractice\n(higher = cleaner)",
           "conf_elections": "Confidence in\nelections", "democracy_rating": "How democratic\nthe country is",
           "satisfaction": "Satisfaction with\npolitical system"}

def dot_whisker(ax, series, labels, xlabel, ref=0.0, log=False):
    """series: list of (name, [(est, lo, hi), ...]) in label order (top to bottom)."""
    n, k = len(labels), len(series)
    off = [(j - (k - 1) / 2) * 0.22 for j in range(k)]
    for j, (name, vals) in enumerate(series):
        ys = [n - 1 - i - off[j] for i in range(n)]   # first series on top
        for y, (e, lo, hi) in zip(ys, vals):
            ax.plot([lo, hi], [y, y], color=C[j], lw=1.6, solid_capstyle="round", zorder=2)
        ax.scatter([v[0] for v in vals], ys, s=34, marker=MK[j], color=C[j],
                   edgecolor="white", linewidth=1.2, zorder=3, label=name)
    ax.axvline(ref, color=ZERO, lw=0.8, ls="--", zorder=1)
    ax.set_yticks(range(n)); ax.set_yticklabels(labels[::-1])
    ax.set_ylim(-0.6, n - 0.4)
    if log: ax.set_xscale("log")
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(xlabel)

# ---------------- Figure 1 (H1, H2): party gaps vs PTI in SD units ----------------
zp, zm = rows("s3_p4_zproc"), rows("s3_p4_zmal")
def sd_row(key, i):          # regime outcomes: CI rescaled by the outcome SD (est / est_in_SD)
    g = R["s3_p5"][key]["gaps"][i][1]
    sd = g["adj"] / g["adj_in_SD"]
    return (g["adj_in_SD"], g["adj_low"] / sd, g["adj_high"] / sd)
fig1 = {}
for i, party in enumerate(["PML-N", "PPP"]):
    term = f"party{party}"
    fig1[party] = [(zp[term]["estimate"], zp[term]["ci_low"], zp[term]["ci_high"]),
                   (zm[term]["estimate"], zm[term]["ci_low"], zm[term]["ci_high"])] + \
                  [sd_row(k, i) for k in OUTCOMES[2:]]
fig, ax = plt.subplots(figsize=(6.2, 3.6))
dot_whisker(ax, [("PML-N supporters", fig1["PML-N"]), ("PPP supporters", fig1["PPP"])],
            [OUT_LAB[k] for k in OUTCOMES],
            "Difference from PTI supporters (standard deviations), with 95% confidence interval")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=2, fontsize=8.5)
ax.set_title("Below 0 = less favourable view than PTI supporters", loc="left", color="#4a4a46", fontsize=8.5)
fig.savefig(F / "Figure1_party_gaps.png"); plt.close(fig)

# ---------------- Figure 2 (H3): four groups vs double losers in SD units ----------------
GROUPS = ["National winner", "National-only winner", "Provincial-only winner"]
fig2 = {g: [] for g in GROUPS}
for k in OUTCOMES:
    rr = dict(R["s4_p2"][k]["rows"])
    for g in GROUPS:
        v = rr["group4" + g]; sd = v["estimate"] / v["in_SD"]
        fig2[g].append((v["in_SD"], v["ci_low"] / sd, v["ci_high"] / sd))
fig, ax = plt.subplots(figsize=(6.2, 4.0))
dot_whisker(ax, [("National winners (PTI, Punjab and KP)", fig2[GROUPS[0]]),
                 ("National-only winners (PTI, Sindh and Balochistan)", fig2[GROUPS[1]]),
                 ("Provincial-only winners (PPP, Sindh)", fig2[GROUPS[2]])],
            [OUT_LAB[k] for k in OUTCOMES],
            "Difference from double losers (standard deviations), with 95% confidence interval")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=1, fontsize=8.5)
ax.set_title("Above 0 = more favourable view than double losers (PML-N, and PPP outside Sindh)",
             loc="left", color="#4a4a46", fontsize=8.5)
fig.savefig(F / "FigureA1_winner_groups.png"); plt.close(fig)

# ---------------- Figure 3 (H4): item gap overall vs at the same underlying rating -------------
ITEMS = ["pf_counted", "pf_officials", "pf_journalists", "pf_choice"]
ITEM_LAB = {"pf_counted": "Votes are counted fairly", "pf_officials": "Election officials are fair",
            "pf_journalists": "Journalists provide\nfair coverage", "pf_choice": "Voters are offered\na genuine choice"}
ol, dif = rows("s3_p6"), rows("s5_p4")
s_ol = [(ol[i]["OR_PMLN"], ol[i]["PMLN_low"], ol[i]["PMLN_high"]) for i in ITEMS]
s_dif = [(dif[i]["OR_PMLN"], dif[i]["boot_low"], dif[i]["boot_high"]) for i in ITEMS]
fig, ax = plt.subplots(figsize=(6.2, 3.1))
dot_whisker(ax, [("Overall gap (ordered logit with controls)", s_ol),
                 ("Gap at the same rating of the other items (item bias test)", s_dif)],
            [ITEM_LAB[i] for i in ITEMS],
            "Odds ratio, PML-N vs PTI supporters (log scale), with 95% cluster-bootstrap interval",
            ref=1.0, log=True)
from matplotlib.ticker import NullFormatter, FixedLocator
ax.xaxis.set_minor_formatter(NullFormatter())
ax.xaxis.set_major_locator(FixedLocator([0.25, 0.5, 1, 2])); ax.set_xticklabels(["0.25", "0.5", "1", "2"])
ax.set_xlim(0.22, 2.2)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.22), fontsize=8.5)
ax.set_title("Below 1 = PML-N supporters give less favourable answers", loc="left", color="#4a4a46", fontsize=8.5)
fig.savefig(F / "Figure2_item_bias.png"); plt.close(fig)

# ---------------- Figure 4 (H5): PML-N - PTI gap within education and interest groups ----------
EG = ["None/primary", "Secondary", "Post-secondary+"]; IG = ["Low interest", "High interest"]
sub = dict(R["s6_sub_educ"]); sub.update(dict(R["s6_sub_int"]))
panels = [("Process fairness", "Process fairness (1–4)"),
          ("How democratic the country is", "How democratic the country is (1–10)")]
fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.1))
for ax, (lab, title) in zip(axes, panels):
    xs, k = [], 0
    for g_i, grp in enumerate([EG, IG]):
        for g in grp:
            v = sub[f"{g} {lab}"]
            x = k + (0.5 if g_i else 0)
            ax.plot([x, x], [v["gap"] - 1.96 * v["se"], v["gap"] + 1.96 * v["se"]],
                    color=C[g_i], lw=1.6, solid_capstyle="round")
            ax.scatter([x], [v["gap"]], s=34, marker=MK[g_i], color=C[g_i],
                       edgecolor="white", linewidth=1.2, zorder=3)
            xs.append((x, {"None/primary": "None/\nprimary", "Secondary": "Second-\nary",
                           "Post-secondary+": "Post-\nsecondary", "Low interest": "Low\ninterest",
                           "High interest": "High\ninterest"}[g]))
            k += 1
    ax.axhline(0, color=ZERO, lw=0.8, ls="--")
    ax.set_xticks([x for x, _ in xs]); ax.set_xticklabels([t for _, t in xs], fontsize=7.5)
    ax.set_title(title, loc="left")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_xlim(-0.5, k + 0.1)
axes[0].set_ylabel("PML-N minus PTI gap\n(scale points, 95% interval)")
for ax in axes:
    ax.text(1, 1.0, "By education", transform=ax.get_xaxis_transform(), ha="center", va="bottom", color="#4a4a46", fontsize=7.5)
    ax.text(4.0, 1.0, "By political interest", transform=ax.get_xaxis_transform(), ha="center", va="bottom", color="#4a4a46", fontsize=7.5)
    ax.set_title(ax.get_title(loc="left"), loc="left", pad=14)
fig.tight_layout()
fig.savefig(F / "Figure3_moderation.png"); plt.close(fig)

json.dump({"fig1": fig1, "fig2": fig2, "fig3": {"ordered_logit": s_ol, "dif": s_dif}},
          open(ROOT / "results" / "figure_data.json", "w"), indent=1)
print("Saved:", sorted(p.name for p in F.glob("*.png")))
