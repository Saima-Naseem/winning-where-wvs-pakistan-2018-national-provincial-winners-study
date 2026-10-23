"""
Reads the stage output logs (R, Stages 1-6; Python, Stage 7) and pulls every number
needed for the paper tables and figures into results/results.json.
No number is typed by hand: each value is read from the log text.
"""
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
OUT = ROOT / "results"; OUT.mkdir(exist_ok=True)

def read(name):
    return (LOGS / name).read_text(encoding="utf-8", errors="replace").replace("\r", "")

def num(tok):
    tok = tok.strip()
    if tok in ("NA", "<NA>", "NaN"): return None
    if tok in ("TRUE", "FALSE"): return tok == "TRUE"
    return float(tok)

def block(text, marker, n_text=0, occurrence=1, skip_header_lines=0, cols=None):
    """Table after the line containing `marker`: first non-empty line is the header,
    rows run until the next empty line. Returns list of (label, {col: value})."""
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if marker in l]
    if len(hits) < occurrence:
        raise ValueError(f"marker not found: {marker!r} (occurrence {occurrence})")
    i = hits[occurrence - 1] + 1
    while lines[i].strip() == "": i += 1
    i += skip_header_lines
    header = lines[i].split()
    num_cols = cols if cols else header[n_text:]
    rows = []
    i += 1
    while i < len(lines) and lines[i].strip() != "":
        toks = lines[i].split()
        if all(re.fullmatch(r"<.*>", t) for t in toks):   # tibble column-type line
            i += 1; continue
        vals = toks[-len(num_cols):]
        label = " ".join(toks[:-len(num_cols)])
        try:
            rows.append((label, {c: num(v) for c, v in zip(num_cols, vals)}))
        except ValueError:          # a text line directly under the table ends it
            break
        i += 1
    return rows

def named_vector(text, marker, labels, occurrence=1):
    """R named vector printed as a label line then a value line (labels may contain spaces)."""
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if marker in l]
    i = hits[occurrence - 1] + 1
    while lines[i].strip() == "": i += 1
    head = lines[i]
    for lab in labels:
        assert lab in head, f"label {lab!r} not in {head!r}"
    vals = lines[i + 1].split()
    return dict(zip(labels, [num(v) for v in vals]))

def after(text, pattern, occurrence=1):
    m = list(re.finditer(pattern, text))
    return m[occurrence - 1].group(1)

R = {}
# ---------------- Stage 1 ----------------
s1 = read("stage1_log.txt")
R["s1_party"] = named_vector(s1, "=== Party preference ===",
                             ["Other", "PML-N", "PPP", "PTI", "Would not vote", "<NA>"])
R["s1_province"] = named_vector(s1, "=== Province ===", ["Balochistan", "KP", "Punjab", "Sindh"])
R["s1_party_by_prov"] = block(s1, "=== Party by province ===")
R["s1_group_by_prov"] = block(s1, "=== Four-way grouping by province ===")
R["s1_missing"] = block(s1, "=== Share missing (DK or NA) by party ===", n_text=1, skip_header_lines=1)
R["s1_dk"] = block(s1, "=== Share answering 'don't know' by party ===", n_text=1, skip_header_lines=1)
R["s1_means"] = block(s1, "=== Direction check", n_text=1, skip_header_lines=1)
R["s1_days"] = [int(after(s1, r"min-max: (\d+) to")), int(after(s1, r"to (\d+) \n"))]
# tibble rows start with a row number: "1 Other 272 ..." -> strip it
for k in ("s1_missing", "s1_dk", "s1_means"):
    R[k] = [(re.sub(r"^\d+ ", "", lab), v) for lab, v in R[k]]

# ---------------- Stage 2 ----------------
s2 = read("stage2_log.txt")
R["s2_complete"] = int(after(s2, r"Complete cases on all nine items: (\d+)"))
R["s2_counts"] = block(s2, "Answer counts per item:")
R["s2_cor"] = block(s2, "Spearman correlations among the nine items:")
R["s2_bartlett"] = {"chi2": float(after(s2, r"chi-square = ([\d.]+) \| df = 36")),
                    "df": 36}
R["s2_kmo_overall"] = float(after(s2, r"Overall KMO: ([\d.]+)"))
R["s2_kmo_items"] = block(s2, "KMO per item:")
R["s2_det"] = float(after(s2, r"Determinant of the correlation matrix: ([\d.]+)"))
R["s2_load2"] = block(s2, "Loadings (rows = items, columns = factors):")
R["s2_factor_cor"] = float(after(s2, r"Correlation between the two factors: (-?[\d.]+)"))
R["s2_communal"] = block(s2, "Communalities (higher = better explained):")
R["s2_eigen"] = [float(x) for x in after(s2, r"Eigenvalues:\n\[1\] ([\d. ]+)").split()]
R["s2_parallel"] = block(s2, "Parallel analysis (real eigenvalue", n_text=0)
R["s2_fitcomp"] = block(s2, "Comparison of 1, 2 and 3 factors:")
R["s2_load3"] = block(s2, "Three-factor loadings:")
R["s2_fcor3"] = block(s2, "Correlations between the three factors:")
R["s2_uniq3"] = block(s2, "Uniquenesses (values below 0.05")
R["s2_scale_desc"] = block(s2, "Scale descriptives:")
R["s2_rel_proc_head"] = after(s2, r"PROCESS FAIRNESS scale \| respondents: (\d+)")
R["s2_alpha"] = {"process": float(after(s2, r"items: 4 \n  alpha = ([\d.]+)")),
                 "malpractice": float(after(s2, r"items: 5 \n  alpha = ([\d.]+)")),
                 "process_iic": float(after(s2, r"average inter-item correlation = ([\d.]+)", 1)),
                 "malpractice_iic": float(after(s2, r"average inter-item correlation = ([\d.]+)", 2)),
                 "process_n": int(after(s2, r"PROCESS FAIRNESS scale \| respondents: (\d+)")),
                 "malpractice_n": int(after(s2, r"MALPRACTICE scale \| respondents: (\d+)"))}
R["s2_rel_proc"] = block(s2, "PROCESS FAIRNESS scale |", n_text=1, skip_header_lines=1)
R["s2_rel_mal"] = block(s2, "MALPRACTICE scale |", n_text=1, skip_header_lines=1)
R["s2_scale_cor"] = float(after(s2, r"Correlation between the two scales \(Spearman\): (-?[\d.]+)"))

# ---------------- Stage 3 ----------------
s3 = read("stage3_log.txt")
R["s3_valid"] = block(s3, "Valid scale scores by party:")
R["s3_rawmeans"] = block(s3, "Raw scale means by party:")
R["s3_p2_proc"] = block(s3, "--- Process fairness ~ party")
R["s3_p2_mal"] = block(s3, "--- Malpractice ~ party")
R["s3_p2_N"] = [int(after(s3, r"Process fairness ~ party \| N = (\d+)")),
                int(after(s3, r"Malpractice ~ party \| N = (\d+)"))]
R["s3_psus"] = int(after(s3, r"PSUs = (\d+)"))
R["s3_p3_N"] = [int(after(s3, r"Respondents in model: (\d+)", 1)), int(after(s3, r"Respondents in model: (\d+)", 2))]
R["s3_p3_r2"] = [[float(x) for x in after(s3, r"unadjusted vs adjusted: ([\d.]+ vs [\d.]+)", k).split(" vs ")] for k in (1, 2)]
R["s3_p3_proc"] = block(s3, "Full adjusted model:", occurrence=1)
R["s3_p3_mal"] = block(s3, "Full adjusted model:", occurrence=2)
R["s3_p3_unadj_proc"] = block(s3, "Party coefficients, unadjusted vs adjusted", occurrence=1)
R["s3_p3_unadj_mal"] = block(s3, "Party coefficients, unadjusted vs adjusted", occurrence=2)
R["s3_p4_N"] = int(after(s3, r"Respondents with both scales and all controls: (\d+)"))
R["s3_p4_zproc"] = block(s3, "Adjusted gap vs PTI, process fairness (SD units)")
R["s3_p4_zmal"] = block(s3, "Adjusted gap vs PTI, malpractice (SD units)")
R["s3_p4_diff"] = block(s3, "Positive = malpractice gap is larger")
R["s3_p4_diff_unadj"] = block(s3, "--- H2 TEST, unadjusted ---")
reg = {}
for k, (key, lab) in enumerate([("conf_elections", "Confidence in elections (1-4)"),
                                ("democracy_rating", "How democratic the country is (1-10)"),
                                ("satisfaction", "Satisfaction with political system (1-10)")], start=1):
    reg[key] = {"N": int(after(s3, re.escape(lab) + r" \| N = (\d+)")),
                "raw": block(s3, "Raw means by party:", occurrence=k),
                "gaps": block(s3, "Gap vs PTI (scale points)", occurrence=k)}
R["s3_p5"] = reg
R["s3_p6"] = block(s3, "Odds ratios vs PTI (adjusted; 95% cluster-bootstrap CI)", n_text=1)

# ---------------- Stage 4 ----------------
s4 = read("stage4_log.txt")
R["s4_sizes"] = named_vector(s4, "Group sizes:", ["National winner", "National-only winner",
                                                 "Provincial-only winner", "Double loser"])
R["s4_valid"] = block(s4, "Valid scale scores per group:", cols=["National winner", "National-only winner", "Provincial-only winner", "Double loser"])
R["s4_rawmeans"] = block(s4, "Raw scale means by group:", cols=["National winner", "National-only winner", "Provincial-only winner", "Double loser"])
out4 = {}
for key, lab in [("scale_process", "--- Process fairness (1-4) | N"),
                 ("scale_malprac", "--- Malpractice (1-4, higher = cleaner) | N"),
                 ("conf_elections", "--- Confidence in elections (1-4) | N"),
                 ("democracy_rating", "--- How democratic the country is (1-10) | N"),
                 ("satisfaction", "--- Satisfaction with political system (1-10) | N")]:
    out4[key] = {"N": int(after(s4, re.escape(lab) + r" = (\d+) \| contrasts")),
                 "rows": block(s4, lab + " = ", occurrence=1)}
R["s4_p2"] = out4
prov = {}
for p_i, prov_name in enumerate(["Punjab", "Sindh"]):
    prov[prov_name] = {}
    for key, lab in [("scale_process", "--- Process fairness (1-4) | N"),
                     ("scale_malprac", "--- Malpractice (1-4, higher = cleaner) | N"),
                     ("conf_elections", "--- Confidence in elections (1-4) | N"),
                     ("democracy_rating", "--- How democratic the country is (1-10) | N"),
                     ("satisfaction", "--- Satisfaction with political system (1-10) | N")]:
        occ = 2 + p_i     # occurrence 1 is Piece 2 (four groups); 2 = Punjab; 3 = Sindh
        line = [l for l in s4.split("\n") if l.startswith(lab)][occ - 1]
        prov[prov_name][key] = {"N": int(re.search(r"N = (\d+)", line).group(1)),
                                "PSUs": int(re.search(r"PSUs = (\d+)", line).group(1)),
                                "rows": block(s4, lab, occurrence=occ)}
R["s4_p3"] = prov
R["s4_p3_n"] = {"Punjab": named_vector(s4, "Respondents by party:", ["PTI", "PML-N", "PPP"], 1),
                "Sindh": named_vector(s4, "Respondents by party:", ["PTI", "PPP"], 2)}
R["s4_p4_prov"] = named_vector(s4, "PPP supporters by province:", ["Balochistan", "KP", "Punjab", "Sindh"])
# PPP Sindh vs elsewhere: rows "<outcome> <spec words> N gap se low high p in_SD"
lines4 = s4.split("\n")
i = [k for k, l in enumerate(lines4) if l.startswith("PPP in Sindh minus PPP elsewhere")][0] + 2
ppp = []
while i < len(lines4) and lines4[i].strip():
    t = lines4[i].split()
    ppp.append({"outcome": t[0], "spec": " ".join(t[1:-7]),
                **dict(zip(["N", "gap", "se", "low", "high", "p", "in_SD"], [num(x) for x in t[-7:]]))})
    i += 1
R["s4_p4"] = ppp

# ---------------- Stage 5 ----------------
s5 = read("stage5_log.txt")
R["s5_valid"] = block(s5, "Valid cases (item and rest score present):")
R["s5_itemmeans"] = block(s5, "Item means by party:")
R["s5_restmeans"] = block(s5, "Rest-score means by party:")
R["s5_itemrest"] = block(s5, "Item-rest correlation within party (Spearman):")
R["s5_p2"] = block(s5, "Effect size (change in Nagelkerke R2)", n_text=1, occurrence=1)
R["s5_p3"] = block(s5, "Effect size (change in Nagelkerke R2)", n_text=2, occurrence=2)
R["s5_p4"] = block(s5, "95% PSU-cluster-bootstrap interval:", n_text=1)
# matched_on text is a single token, so the label holds "item matched_on"
R["s5_p3"] = [(lab.split()[0], {**v, "matched_on": lab.split()[1]}) for lab, v in R["s5_p3"]]

# ---------------- Stage 6 ----------------
s6 = read("stage6_log.txt")
R["s6_educ_dist"] = block(s6, "Education (ISCED level) distribution:")
R["s6_int_dist"] = block(s6, "Political interest distribution:")
R["s6_mods"] = block(s6, "Mean education, mean interest, share female, by party:")
R["s6_cor"] = float(after(s6, r"Spearman correlation, education and interest: ([\d.]+)"))
R["s6_educ"] = block(s6, "--- Party x EDUCATION (per 1 SD) ---", n_text=1)
R["s6_int"] = block(s6, "--- Party x POLITICAL INTEREST (per 1 SD) ---", n_text=1)
R["s6_sex"] = block(s6, "--- Party x SEX (women vs men) ---", n_text=1)
R["s6_sub_educ"] = block(s6, "--- PML-N minus PTI gap within EDUCATION groups (adjusted) ---", n_text=2)
R["s6_sub_int"] = block(s6, "--- PML-N minus PTI gap within INTEREST groups (adjusted) ---", n_text=2)

# ---------------- Stage 7 ----------------
s7 = read("stage7_log.txt")
R["s7_summary"] = re.findall(r"(Piece [^:]+): (?:variables compared|coefficient rows checked): (\d+) \| (?:with any mismatch|needing a check): (\d+)", s7)
R["s7_software"] = after(s7, r"Software: (.+)")

(OUT / "results.json").write_text(json.dumps(R, indent=1), encoding="utf-8")
print("Saved results.json with", len(R), "entries")
