# =============================================================================
# STAGE 7: Independent verification in Python
# Paper:  Winning where? National and provincial differences in perceptions
#         of Pakistan's 2018 election
# Input:  stage2_clean.csv (from R, Stages 1-2); WVS_Pak_Data.xlsx (Piece 2)
# Output: stage7_log.txt (console log; overwritten on every run)
# Run:    Command Prompt:  python stage7_python_verification.py
# =============================================================================
import os
import sys

# ---- 0. SETTINGS (edit only this block) --------------------------------------
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the repository folder

# ---- 1. SETUP -----------------------------------------------------------------
os.chdir(PROJECT_DIR)

class Tee:
    """Send everything printed to both the screen and the log file."""
    def __init__(self, *streams):
        self.streams = streams
    def write(self, text):
        for s in self.streams:
            s.write(text)
    def flush(self):
        for s in self.streams:
            s.flush()

log = open("logs/stage7_log.txt", "w", encoding="utf-8")
sys.stdout = Tee(sys.__stdout__, log)

# ---- PIECE 1: setup check and match with R group sizes / raw means ------------------
print("\n===== STAGE 7, PIECE 1: setup and match with R =====")

import datetime
print("Run time:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("Python:", sys.version.split()[0])

# 1. Check the libraries (nothing is installed by this script)
missing = []
for name in ["numpy", "pandas", "scipy", "statsmodels", "openpyxl"]:
    try:
        mod = __import__(name)
        print(f"{name:12s} {mod.__version__}")
    except ImportError:
        missing.append(name)
        print(f"{name:12s} NOT INSTALLED")
if missing:
    print("\nMissing libraries:", ", ".join(missing))
    print("Install with:  pip install " + " ".join(missing))
    sys.stdout = sys.__stdout__; log.close(); sys.exit()

import numpy as np
import pandas as pd
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

# 2. Load the file made by R in Stage 2
df = pd.read_csv("data/stage2_clean.csv")
print("\nRows:", len(df), "| Columns:", df.shape[1])

# 3. Comparison sample (as in Stage 3): PTI, PML-N, PPP supporters
d3 = df[df["party"].isin(["PTI", "PML-N", "PPP"])].copy()
print("\nRespondents by party (R: PTI 685, PML-N 368, PPP 299):")
print(d3["party"].value_counts().reindex(["PTI", "PML-N", "PPP"]))

# 4. Valid scale scores and raw means by party
#    R: process 2.98 / 2.77 / 2.68; malpractice 2.26 / 1.99 / 2.47
g = d3.groupby("party")[["scale_process", "scale_malprac"]]
print("\nValid scale scores by party (R: process 664/357/288; malpractice 657/356/284):")
print(g.count().reindex(["PTI", "PML-N", "PPP"]))
print("\nRaw scale means by party:")
print(g.mean().reindex(["PTI", "PML-N", "PPP"]).round(2))

# 5. Four-way groups (as in Stage 4)
#    R: National winner 553, National-only winner 132, Provincial-only winner 216, Double loser 451
d4 = df[df["group4"].notna()].copy()
order = ["National winner", "National-only winner", "Provincial-only winner", "Double loser"]
print("\nGroup sizes (R: 553, 132, 216, 451):")
print(d4["group4"].value_counts().reindex(order))
print("\nRaw means by group:")
cols = ["scale_process", "scale_malprac", "conf_elections", "democracy_rating", "satisfaction"]
print(d4.groupby("group4")[cols].mean().reindex(order).round(2).T)

# ---- PIECE 2: independent rebuild of the variables from the raw Excel file ----------
print("\n===== STAGE 7, PIECE 2: independent recode from raw data vs R =====")

raw = pd.read_excel("data/WVS_Pak_Data.xlsx", sheet_name="original")
raw.columns = [str(c).split(":")[0].strip() for c in raw.columns]   # "Q224: ..." -> "Q224"
raw = raw.apply(pd.to_numeric, errors="coerce")
assert len(raw) == 1995 == len(df), "row counts differ"
assert (raw["I_PSU"].values == df["I_PSU"].values).all(), "PSU order differs: rows not aligned"
print("Raw rows:", len(raw), "| row order matches R file (PSU ids identical)")

def clean(x):
    """WVS missing codes are negative -> missing."""
    return x.where(x >= 0)

py = pd.DataFrame(index=raw.index)

# 1. Nine integrity items. Fairness items reversed (5 - x); malpractice items as coded.
for new, q in {"pf_counted": "Q224", "pf_journalists": "Q228",
               "pf_officials": "Q229", "pf_choice": "Q232"}.items():
    py[new] = 5 - clean(raw[q])
for new, q in {"mp_blocked": "Q225", "mp_tvbias": "Q226", "mp_bribery": "Q227",
               "mp_richbuy": "Q230", "mp_violence": "Q231"}.items():
    py[new] = clean(raw[q])

# 2. Regime evaluation
py["conf_elections"]   = 5 - clean(raw["Q76"])
py["democracy_rating"] = clean(raw["Q251"])
py["satisfaction"]     = clean(raw["Q252"])

# 3. Scales: mean of items; at least 2 of 4 (process) or 3 of 5 (malpractice) answered
proc = ["pf_counted", "pf_journalists", "pf_officials", "pf_choice"]
mal  = ["mp_blocked", "mp_tvbias", "mp_bribery", "mp_richbuy", "mp_violence"]
py["scale_process"] = py[proc].mean(axis=1).where(py[proc].notna().sum(axis=1) >= 2)
py["scale_malprac"] = py[mal].mean(axis=1).where(py[mal].notna().sum(axis=1) >= 3)

# 4. Party preference (Q223), province, and the four-way winner/loser group
party_map = {586007: "PTI", 586002: "PML-N", 586001: "PPP", 2: "Would not vote"}
q223 = raw["Q223"]
py["party"] = q223.map(party_map).where(q223.notna() & (q223 >= 0))
py.loc[q223.notna() & (q223 >= 0) & ~q223.isin(list(party_map)), "party"] = "Other"
py["province"] = raw["N_REGION_WVS"].map({586010: "Punjab", 586011: "Sindh",
                                          586012: "KP", 586013: "Balochistan"})
g = pd.Series(np.nan, index=raw.index, dtype=object)
g[(py.party == "PTI")   & py.province.isin(["Punjab", "KP"])]         = "National winner"
g[(py.party == "PTI")   & py.province.isin(["Sindh", "Balochistan"])] = "National-only winner"
g[(py.party == "PPP")   & (py.province == "Sindh")]                   = "Provincial-only winner"
g[(py.party == "PML-N")]                                              = "Double loser"
g[(py.party == "PPP")   & (py.province != "Sindh")]                   = "Double loser"
py["group4"] = g

# 5. Controls
py["female"]  = (raw["Q260"] == 2).astype(float).where(raw["Q260"].notna())
py["age"]     = clean(raw["Q262"])
py["educ"]    = clean(raw["Q275"])
py["income3"] = pd.Series(np.select([raw.Q288.between(1, 3), raw.Q288.between(4, 7),
                                     raw.Q288.between(8, 10)], ["Low", "Medium", "High"],
                                    default=""), index=raw.index).replace("", np.nan)
py["rural"]   = (raw["H_URBRURAL"] == 2).astype(float).where(raw["H_URBRURAL"].notna())
tongue = {586001: "Punjabi", 586004: "Sindhi", 586006: "Pashto", 586008: "Seraiki",
          586003: "Baluchi", 586007: "Hindko", 586009: "Hindko", 586005: "Other", 586999: "Other"}
py["mothertongue"] = raw["Q290"].map(tongue)
py["interest"]   = 5 - clean(raw["Q199"])
dates = pd.to_datetime(raw["J_INTDATE"].astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
py["days_since"] = (dates - pd.Timestamp("2018-07-25")).dt.days.astype(float)

# 6. Compare every variable with the R file (missing matches missing)
def n_mismatch(a, b):
    if not (pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b)):
        a, b = a.astype(object).where(a.notna(), "<NA>"), b.astype(object).where(b.notna(), "<NA>")
        return int((a.astype(str) != b.astype(str)).sum())       # text variables
    a, b = pd.to_numeric(a), pd.to_numeric(b)
    same = np.isclose(a, b, rtol=0, atol=1e-9) | (a.isna() & b.isna())
    return int((~same).sum())                                     # numeric variables

rows = [(v, n_mismatch(py[v], df[v])) for v in py.columns]
cmp_tab = pd.DataFrame(rows, columns=["variable", "mismatches"])
print("\nPython recode vs R (mismatches should all be 0):")
print(cmp_tab.to_string(index=False))
print("\nVariables compared:", len(cmp_tab), "| variables with any mismatch:",
      int((cmp_tab.mismatches > 0).sum()))



# ---- PIECE 3: Stage 3 models re-run with statsmodels vs R ---------------------------
print("\n===== STAGE 7, PIECE 3: Stage 3 models (statsmodels) vs R =====")
import statsmodels.formula.api as smf

# 1. Comparison sample and variables (same coding as R)
d3p = df[df["party"].isin(["PTI", "PML-N", "PPP"])].copy()
d3p["party"] = pd.Categorical(d3p["party"], categories=["PTI", "PML-N", "PPP"])   # PTI = reference
d3p["income3"] = pd.Categorical(d3p["income3"], categories=["Low", "Medium", "High"])
d3p["mothertongue"] = pd.Categorical(d3p["mothertongue"],
    categories=["Punjabi", "Sindhi", "Pashto", "Seraiki", "Baluchi", "Hindko", "Other"])
d3p["age10"] = d3p["age"] / 10
controls = ["age10", "female", "educ", "income3", "rural", "mothertongue", "interest", "days_since"]

def fit_cluster(y, terms, data):
    """OLS with standard errors clustered by PSU (CR1 correction, t-tests with PSUs-1 df)."""
    dat = data.dropna(subset=[y] + terms)
    m = smf.ols(f"{y} ~ " + " + ".join(terms), data=dat).fit(
        cov_type="cluster", cov_kwds={"groups": dat["I_PSU"].values, "use_correction": True},
        use_t=True)
    return m, dat

# 2. R results copied from the Stage 3 log: (label, outcome, adjusted?, N, [(term, est, se)])
R_RESULTS = [
    ("Piece 2 process, unadjusted",    "scale_process",    False, 1309, [("PML-N", -0.206, 0.065), ("PPP", -0.298, 0.081)]),
    ("Piece 2 malpractice, unadjusted","scale_malprac",    False, 1297, [("PML-N", -0.269, 0.064), ("PPP",  0.212, 0.096)]),
    ("Piece 3 process, adjusted",      "scale_process",    True,  1209, [("PML-N", -0.270, 0.058), ("PPP", -0.197, 0.088)]),
    ("Piece 3 malpractice, adjusted",  "scale_malprac",    True,  1201, [("PML-N", -0.147, 0.053), ("PPP",  0.073, 0.087)]),
    ("Piece 5 confidence, adjusted",   "conf_elections",   True,  1189, [("PML-N", -0.215, 0.076), ("PPP", -0.082, 0.106)]),
    ("Piece 5 democracy, adjusted",    "democracy_rating", True,  1227, [("PML-N", -2.147, 0.238), ("PPP", -0.645, 0.277)]),
    ("Piece 5 satisfaction, adjusted", "satisfaction",     True,  1235, [("PML-N", -2.351, 0.228), ("PPP", -0.675, 0.241)]),
]

rows = []
for label, y, adjusted, n_r, terms in R_RESULTS:
    rhs = ["party"] + (controls if adjusted else [])
    m, dat = fit_cluster(y, rhs, d3p)
    for term, est_r, se_r in terms:
        name = f"party[T.{term}]"
        est_p, se_p = m.params[name], m.bse[name]
        ok = (len(dat) == n_r) and abs(est_p - est_r) < 0.0011 and abs(se_p - se_r) < 0.0011
        rows.append([label, term, len(dat), n_r, round(est_p, 3), est_r,
                     round(se_p, 3), se_r, round(m.pvalues[name], 3), "OK" if ok else "CHECK"])

tab = pd.DataFrame(rows, columns=["model", "party", "N_py", "N_R", "est_py", "est_R",
                                  "se_py", "se_R", "p_py", "status"])
print("\nPython (statsmodels) vs R, gap vs PTI:")
print(tab.to_string(index=False))
print("\nRows checked:", len(tab), "| rows needing a check:", int((tab.status != "OK").sum()))


# ---- PIECE 4: H2 test (Stage 3) and four-group models (Stage 4) vs R ----------------
print("\n===== STAGE 7, PIECE 4: H2 test and Stage 4 group models vs R =====")

def compare(spec_list, fitter):
    """spec_list items: (label, N_R, [(coef_name, label_term, est_R, se_R)], model_result_tuple)."""
    rows = []
    for label, n_r, terms, (m, dat) in spec_list:
        for name, term, est_r, se_r in terms:
            est_p, se_p = m.params[name], m.bse[name]
            ok = (len(dat) == n_r) and abs(est_p - est_r) < 0.0011 and abs(se_p - se_r) < 0.0011
            rows.append([label, term, len(dat), n_r, round(est_p, 3), est_r,
                         round(se_p, 3), se_r, round(m.pvalues[name], 3), "OK" if ok else "CHECK"])
    return pd.DataFrame(rows, columns=["model", "term", "N_py", "N_R", "est_py", "est_R",
                                       "se_py", "se_R", "p_py", "status"])

# 1. H2: standardize both scales on the same 1,191 respondents; model their difference
need = ["scale_process", "scale_malprac", "party"] + controls
dat2 = d3p.dropna(subset=need).copy()
dat2["z_proc"] = (dat2["scale_process"] - dat2["scale_process"].mean()) / dat2["scale_process"].std()
dat2["z_mal"]  = (dat2["scale_malprac"] - dat2["scale_malprac"].mean()) / dat2["scale_malprac"].std()
dat2["z_diff"] = dat2["z_proc"] - dat2["z_mal"]
P, Q = "party[T.PML-N]", "party[T.PPP]"
h2 = [
    ("H2 z_process, adjusted",   1191, [(P, "PML-N", -0.353, 0.076), (Q, "PPP", -0.246, 0.116)],
        fit_cluster("z_proc", ["party"] + controls, dat2)),
    ("H2 z_malpractice, adjusted", 1191, [(P, "PML-N", -0.198, 0.067), (Q, "PPP", 0.086, 0.109)],
        fit_cluster("z_mal", ["party"] + controls, dat2)),
    ("H2 difference, adjusted",  1191, [(P, "PML-N", -0.155, 0.114), (Q, "PPP", -0.332, 0.188)],
        fit_cluster("z_diff", ["party"] + controls, dat2)),
    ("H2 difference, unadjusted", 1191, [(P, "PML-N", 0.035, 0.139), (Q, "PPP", -0.755, 0.211)],
        fit_cluster("z_diff", ["party"], dat2)),
]
tab_h2 = compare(h2, fit_cluster)
print("\nH2 test, Python vs R:")
print(tab_h2.to_string(index=False))

# 2. Stage 4: four groups vs Double loser (adjusted)
d4p = df[df["group4"].notna()].copy()
d4p["group4"] = pd.Categorical(d4p["group4"], categories=["Double loser", "National winner",
                               "National-only winner", "Provincial-only winner"])
d4p["income3"] = pd.Categorical(d4p["income3"], categories=["Low", "Medium", "High"])
d4p["mothertongue"] = pd.Categorical(d4p["mothertongue"],
    categories=["Punjabi", "Sindhi", "Pashto", "Seraiki", "Baluchi", "Hindko", "Other"])
d4p["age10"] = d4p["age"] / 10
G = lambda g: f"group4[T.{g}]"
s4_R = {   # outcome: (N_R, [(group, est_R, se_R)]) from the Stage 4 log, Piece 2
    "scale_process":    (1209, [("National winner", 0.289, 0.060), ("National-only winner", -0.189, 0.128), ("Provincial-only winner", -0.267, 0.131)]),
    "scale_malprac":    (1201, [("National winner", 0.087, 0.052), ("National-only winner", 0.561, 0.143), ("Provincial-only winner", 0.570, 0.144)]),
    "conf_elections":   (1189, [("National winner", 0.250, 0.076), ("National-only winner", -0.598, 0.150), ("Provincial-only winner", -0.507, 0.154)]),
    "democracy_rating": (1227, [("National winner", 2.001, 0.241), ("National-only winner", 1.072, 0.339), ("Provincial-only winner", 0.930, 0.380)]),
    "satisfaction":     (1235, [("National winner", 2.139, 0.227), ("National-only winner", 1.881, 0.381), ("Provincial-only winner", 1.625, 0.398)]),
}
s4 = [(f"Stage 4 {y}", n_r, [(G(g), g, e, s) for g, e, s in terms],
       fit_cluster(y, ["group4"] + controls, d4p))
      for y, (n_r, terms) in s4_R.items()]
tab_s4 = compare(s4, fit_cluster)
print("\nStage 4 four-group models vs Double loser, Python vs R:")
print(tab_s4.to_string(index=False))

n_check = int((tab_h2.status != "OK").sum() + (tab_s4.status != "OK").sum())
print("\nRows checked:", len(tab_h2) + len(tab_s4), "| rows needing a check:", n_check)


# ---- PIECE 5: within-province models and PPP Sindh vs elsewhere vs R ----------------
print("\n===== STAGE 7, PIECE 5: within-province and PPP comparisons vs R =====")

def fit_sub(y, terms, data):
    """Like fit_cluster, but drops category levels absent from the estimation sample."""
    dat = data.dropna(subset=[y] + terms).copy()
    for c in dat.columns:
        if isinstance(dat[c].dtype, pd.CategoricalDtype):
            dat[c] = dat[c].cat.remove_unused_categories()
    m = smf.ols(f"{y} ~ " + " + ".join(terms), data=dat).fit(
        cov_type="cluster", cov_kwds={"groups": dat["I_PSU"].values, "use_correction": True},
        use_t=True)
    return m, dat

def compare2(specs, se_tol=0.0011):
    rows = []
    for label, n_r, terms, (m, dat) in specs:
        for name, term, est_r, se_r in terms:
            est_p, se_p = m.params[name], m.bse[name]
            ok = (len(dat) == n_r) and abs(est_p - est_r) < 0.0011 and abs(se_p - se_r) < se_tol
            rows.append([label, term, len(dat), n_r, round(est_p, 3), est_r,
                         round(se_p, 3), se_r, round(m.pvalues[name], 3), "OK" if ok else "CHECK"])
    return pd.DataFrame(rows, columns=["model", "term", "N_py", "N_R", "est_py", "est_R",
                                       "se_py", "se_R", "p_py", "status"])

# 1. Within Punjab (PTI, PML-N, PPP) and within Sindh (PTI, PPP), adjusted, PTI = reference
punjab = d3p[d3p["province"] == "Punjab"]
sindh  = d3p[(d3p["province"] == "Sindh") & d3p["party"].isin(["PTI", "PPP"])].copy()
sindh["party"] = pd.Categorical(sindh["party"].astype(str), categories=["PTI", "PPP"])
P, Q = "party[T.PML-N]", "party[T.PPP]"
pun_R = {"scale_process": (732, -0.362, 0.067, -0.250, 0.146), "scale_malprac": (726, -0.103, 0.057, -0.024, 0.112),
         "conf_elections": (717, -0.352, 0.084, -0.059, 0.172), "democracy_rating": (745, -2.539, 0.264, -1.268, 0.458),
         "satisfaction": (753, -2.497, 0.263, -1.396, 0.414)}
sin_R = {"scale_process": (268, -0.086, 0.137), "scale_malprac": (267, 0.084, 0.125),
         "conf_elections": (264, -0.042, 0.158), "democracy_rating": (271, -0.291, 0.414),
         "satisfaction": (271, -0.387, 0.358)}
specs = []
for y, (n, e1, s1, e2, s2) in pun_R.items():
    specs.append((f"Punjab {y}", n, [(P, "PML-N", e1, s1), (Q, "PPP", e2, s2)],
                  fit_sub(y, ["party"] + controls, punjab)))
for y, (n, e, s) in sin_R.items():
    specs.append((f"Sindh {y}", n, [(Q, "PPP", e, s)], fit_sub(y, ["party"] + controls, sindh)))
tab_prov = compare2(specs)
print("\nWithin-province models, Python vs R:")
print(tab_prov.to_string(index=False))

# 2. PPP supporters: Sindh vs elsewhere (no mother-tongue control, as in the R main version)
ppp = d3p[d3p["party"] == "PPP"].copy()
ppp["in_sindh"] = (ppp["province"] == "Sindh").astype(float)
ctrl_nolang = [c for c in controls if c != "mothertongue"]
ppp_R = {"scale_process": (260, -0.389, 0.14), "scale_malprac": (257, 0.607, 0.13),
         "conf_elections": (253, -0.549, 0.15), "democracy_rating": (266, 0.034, 0.48),
         "satisfaction": (266, 0.023, 0.46)}
specs2 = [(f"PPP Sindh vs elsewhere {y}", n, [("in_sindh", "in Sindh", e, s)],
           fit_sub(y, ["in_sindh"] + ctrl_nolang, ppp)) for y, (n, e, s) in ppp_R.items()]
tab_ppp = compare2(specs2, se_tol=0.0051)       # R log printed these SEs to 2 decimals
print("\nPPP in Sindh minus PPP elsewhere, Python vs R:")
print(tab_ppp.to_string(index=False))

n_check = int((tab_prov.status != "OK").sum() + (tab_ppp.status != "OK").sum())
print("\nRows checked:", len(tab_prov) + len(tab_ppp), "| rows needing a check:", n_check)




# ---- SUMMARY OF ALL VERIFICATION PIECES ---------------------------------------------
print("\n===== STAGE 7 SUMMARY =====")
print("Piece 2: variables compared:", len(cmp_tab), "| with any mismatch:", int((cmp_tab.mismatches > 0).sum()))
for name, t in [("Piece 3", tab), ("Piece 4 H2", tab_h2), ("Piece 4 groups", tab_s4),
                ("Piece 5 provinces", tab_prov), ("Piece 5 PPP", tab_ppp)]:
    print(f"{name}: coefficient rows checked: {len(t)} | needing a check: {int((t.status != 'OK').sum())}")
    import statsmodels, scipy
print("Software: Python", sys.version.split()[0], "| pandas", pd.__version__,
      "| statsmodels", statsmodels.__version__, "| numpy", np.__version__, "| scipy", scipy.__version__)

# ---- END (keep these two lines last) -----------------------------------------------
sys.stdout = sys.__stdout__
log.close()


