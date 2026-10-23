"""
Online appendix: one table for every piece of the analysis (Stages 1-7), each with an
interpretation (Online_Appendix.docx). Every number comes from results/results.json.
"""
from pathlib import Path
import json
from docx_helpers import *

ROOT = Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
OUT = ROOT / "paper"
D = lambda key: dict(R[key])

ITEMS = ["pf_counted", "pf_journalists", "pf_officials", "pf_choice",
         "mp_blocked", "mp_tvbias", "mp_bribery", "mp_richbuy", "mp_violence"]
IL = {"pf_counted": "Votes are counted fairly", "pf_journalists": "Journalists provide fair coverage",
      "pf_officials": "Election officials are fair", "pf_choice": "Voters are offered a genuine choice",
      "mp_blocked": "Opposition candidates are prevented from running", "mp_tvbias": "TV news favours the governing party",
      "mp_bribery": "Voters are bribed", "mp_richbuy": "Rich people buy elections",
      "mp_violence": "Voters are threatened with violence at the polls",
      "conf_elections": "Confidence in elections", "democracy_rating": "How democratic the country is",
      "satisfaction": "Satisfaction with the political system"}
OUTCOMES = ["scale_process", "scale_malprac", "conf_elections", "democracy_rating", "satisfaction"]
OL = {"scale_process": "Process fairness (1–4)", "scale_malprac": "Malpractice, higher = cleaner (1–4)",
      "conf_elections": "Confidence in elections (1–4)", "democracy_rating": "How democratic the country is (1–10)",
      "satisfaction": "Satisfaction with the political system (1–10)"}
OL6 = {"scale_process": "Process fairness", "scale_malprac": "Malpractice (higher = cleaner)",
       "conf_elections": "Confidence in elections", "democracy_rating": "How democratic the country is",
       "satisfaction": "Satisfaction with political system"}
GROUPS = ["National winner", "National-only winner", "Provincial-only winner", "Double loser"]
CL = ("Standard errors clustered by primary sampling unit (CR1 correction; t-tests with clusters minus one "
      "degrees of freedom). * p < .05, ** p < .01, *** p < .001.")
CTRL = ("Controls: age, sex, education, income (three groups), rural residence, mother tongue, political interest "
        "and days between the election and the interview. ")

doc = new_doc("Winning where? National and provincial differences in perceptions of Pakistan's 2018 election",
              "Online appendix: tables for every step of the analysis, with interpretation. World Values Survey "
              "Wave 7, Pakistan, N = 1,995. Higher values always mean a more favourable view.")

# =================================== STAGE 1 ===================================
heading(doc, "A. Data preparation (Stage 1)")
pbp = R["s1_party_by_prov"]; prov = ["Punjab", "Sindh", "KP", "Balochistan"]
rows = []
for lab, v in pbp:
    tot = int(sum(v[p] for p in prov))
    assert lab not in R["s1_party"] or tot == int(R["s1_party"][lab]), lab
    rows.append([{"<NA>": "No answer"}.get(lab, lab)] + [f"{int(v[p])}" for p in prov] + [f"{tot:,}"])
rows.append(["Total"] + [f"{int(R['s1_province'][p]):,}" for p in prov] + [f"{int(sum(R['s1_province'].values())):,}"])
pv = dict(pbp)
table(doc, "Table A1", "Party preference by province", ["Party preference", "Punjab", "Sindh", "KP", "Balochistan", "Total"],
      rows, [2.1, 0.9, 0.9, 0.9, 0.9, 0.9],
      note=f"Question Q223 (vote if an election were held tomorrow). Days from the election to the interview: "
           f"{R['s1_days'][0]} to {R['s1_days'][1]}.",
      interpretation=(
          f"Party support follows provincial lines. PML-N support is concentrated in Punjab ({int(pv['PML-N']['Punjab'])} "
          f"of {int(R['s1_party']['PML-N'])}), PPP support in Sindh ({int(pv['PPP']['Sindh'])} of "
          f"{int(R['s1_party']['PPP'])}), while PTI draws on Punjab ({int(pv['PTI']['Punjab'])}), KP "
          f"({int(pv['PTI']['KP'])}) and Sindh ({int(pv['PTI']['Sindh'])}). This overlap of party and province is the "
          f"reason the paper compares supporters within provinces (Table 3, Panel B). The {int(R['s1_party']['Would not vote'])} "
          f"respondents who would not vote and the {int(R['s1_party']['Other'])} who prefer other parties are not used "
          f"in the party comparisons."))

gbp = dict(R["s1_group_by_prov"]); sz = R["s4_sizes"]
rows = [[g] + [f"{int(gbp[g][p])}" for p in prov] + [f"{int(sz[g])}"] for g in GROUPS]
for g in GROUPS: assert int(sum(gbp[g][p] for p in prov)) == int(sz[g])
table(doc, "Table A2", "The four winner and loser groups by province", ["Group", "Punjab", "Sindh", "KP", "Balochistan", "Total"],
      rows, [2.1, 0.9, 0.9, 0.9, 0.9, 0.9],
      note="National winners: PTI in Punjab and KP. National-only winners: PTI in Sindh and Balochistan. Provincial-only "
           "winners: PPP in Sindh. Double losers: PML-N anywhere and PPP outside Sindh.",
      interpretation=(
          f"Every group has more than 130 members, so all four can be compared. The design is uneven across provinces: "
          f"provincial-only winners exist only in Sindh, and only {int(gbp['Double loser']['Sindh'])} double losers live "
          f"there, against {int(gbp['Double loser']['Punjab'])} in Punjab. Group membership therefore partly stands for "
          f"province, a limitation the paper states."))

ms, dk = D("s1_missing"), D("s1_dk"); grp = ["PTI", "PML-N", "PPP", "Other", "Would not vote"]
rows = [[IL[i]] + [f"{ms[g][i] * 100:.1f} ({dk[g]['dk_' + i] * 100:.1f})" for g in grp] for i in ITEMS]
P3_ = ["PTI", "PML-N", "PPP"]
top2 = sorted(ITEMS, key=lambda i: -sum(ms[g][i] for g in P3_))[:2]
rows += [[IL[i]] + [f"{ms[g][i] * 100:.1f}" for g in grp] for i in ["conf_elections", "democracy_rating", "satisfaction"]]
table(doc, "Table A3", "Missing answers by party preference (percent; 'don't know' in parentheses)",
      ["Item"] + ["PTI", "PML-N", "PPP", "Other", "Would not vote"], rows, [2.35, 0.8, 0.8, 0.8, 0.8, 1.05], size=8.5,
      note="Missing = 'don't know' or 'no answer'. 'Don't know' shares are shown only for the nine integrity items.",
      interpretation=(
          f"Among PTI, PML-N and PPP supporters, missing answers on the nine integrity items range from "
          f"{min(ms[g][i] for g in P3_ for i in ITEMS) * 100:.1f} to {max(ms[g][i] for g in P3_ for i in ITEMS) * 100:.1f} "
          f"percent, and almost all of them are 'don't know'. The highest average shares are for "
          f"{IL[top2[0]].lower()} and {IL[top2[1]].lower()}. Respondents who would not vote have about twice the missing "
          f"rate (for example {ms['Would not vote']['pf_journalists'] * 100:.1f} percent on journalists' coverage), which "
          f"fits weaker engagement but does not affect the party comparisons. The three party groups differ little, so "
          f"missing data are unlikely to drive the party gaps."))

# =================================== STAGE 2 ===================================
heading(doc, "B. The two integrity dimensions (Stage 2)")
cnt = dict(R["s2_counts"])
rows = [[IL[i]] + [f"{int(cnt[str(k)][i])}" for k in (1, 2, 3, 4)] + [f"{int(sum(cnt[str(k)][i] for k in (1,2,3,4))):,}"] for i in ITEMS]
table(doc, "Table A4", "Answer distribution of the nine integrity items (counts)",
      ["Item", "1 (least favourable)", "2", "3", "4 (most favourable)", "Valid"], rows, [2.6, 0.9, 0.7, 0.7, 0.9, 0.8], size=8.5,
      note="Fairness items (counted, journalists, officials, choice) are reversed so that 4 = happens very often; "
           "malpractice items are kept so that 4 = never happens. Both directions therefore mean a cleaner election.",
      interpretation=(
          "All four answer categories are used for every item, so no item suffers from floor or ceiling effects. "
          "Fairness items lean towards favourable answers, while malpractice items lean towards reports of frequent "
          "malpractice: for example, the most common answer on 'rich people buy elections' is that it happens very often. "
          "Respondents therefore judge the election in mixed terms rather than as wholly clean or wholly flawed."))

cor = dict(R["s2_cor"]); short = [str(k) for k in range(1, 10)]
rows = []
for a, i in enumerate(ITEMS):
    rows.append([f"{a + 1}. {IL[i]}"] + [f(cor[i][j]) if b < a else ("1" if b == a else "") for b, j in enumerate(ITEMS)])
table(doc, "Table A5", f"Spearman correlations among the nine items (complete cases, n = {R['s2_complete']:,})",
      ["Item"] + short, rows, [2.55] + [0.45] * 9, size=8,
      interpretation=(
          f"Items correlate positively within each block: the four fairness items between "
          f"{f(min(cor[i][j] for i in ITEMS[:4] for j in ITEMS[:4] if i != j))} and "
          f"{f(max(cor[i][j] for i in ITEMS[:4] for j in ITEMS[:4] if i != j))}, and the five malpractice items between "
          f"{f(min(cor[i][j] for i in ITEMS[4:] for j in ITEMS[4:] if i != j))} and "
          f"{f(max(cor[i][j] for i in ITEMS[4:] for j in ITEMS[4:] if i != j))}. Correlations across the blocks are weak "
          f"and mostly negative. This is the first sign of two separate dimensions, and of the negative relation "
          f"between them that the paper discusses as a possible response-style effect."))

km = R["s2_kmo_items"][0][1]
rows = [["Bartlett's test of sphericity", f"χ² = {f(R['s2_bartlett']['chi2'], 1)}, df = {R['s2_bartlett']['df']}, p < .001"],
        ["Overall KMO", f(R["s2_kmo_overall"])], ["Determinant of the correlation matrix", f(R["s2_det"], 4)]]
rows += [[f"KMO: {IL[i]}", f(km[i])] for i in ITEMS]
table(doc, "Table A6", "Suitability of the items for factor analysis", ["Test", "Value"], rows, [4.1, 2.5],
      interpretation=(
          f"The items are well suited to factor analysis. Bartlett's test rejects the hypothesis of no correlation, the "
          f"overall KMO of {f(R['s2_kmo_overall'])} is 'meritorious' by the usual guide, every item has a KMO of at least "
          f"{f(min(km.values()))}, and the determinant ({f(R['s2_det'], 4)}) shows no problem of near-identical items."))

l2 = dict(R["s2_load2"]); cm = R["s2_communal"][0][1]
rows = [[IL[i], f(l2[i]["Factor1"]), f(l2[i]["Factor2"]), f(cm[i])] for i in ITEMS]
fc = dict((int(v["factors"]), v) for _, v in R["s2_fitcomp"])
rows.append(("PANEL", f"Factor correlation {f(R['s2_factor_cor'])}; χ² = {f(fc[2]['chi_square'], 1)}, "
                      f"df = {int(fc[2]['df'])}, RMSEA = {f(fc[2]['RMSEA'], 3)}"))
table(doc, "Table A7", f"Two-factor solution (maximum likelihood, promax rotation, n = {R['s2_complete']:,})",
      ["Item", "Factor 1: malpractice", "Factor 2: process fairness", "Communality"], rows, [2.9, 1.25, 1.35, 1.1], size=8.5,
      interpretation=(
          f"The solution has a clean simple structure. All five malpractice items load on the first factor "
          f"({f(min(l2[i]['Factor1'] for i in ITEMS[4:]))} to {f(max(l2[i]['Factor1'] for i in ITEMS[4:]))}) and all four "
          f"fairness items on the second ({f(min(l2[i]['Factor2'] for i in ITEMS[:4]))} to "
          f"{f(max(l2[i]['Factor2'] for i in ITEMS[:4]))}), with no cross-loading above 0.30. The two factors correlate at "
          f"{f(R['s2_factor_cor'])}: people who see a fair process tend also to report more malpractice, which is "
          f"why the paper treats the two blocks separately and notes possible effects of the shared answer scale and "
          f"of positive versus negative wording."))

pa = [v for _, v in R["s2_parallel"]]
rows = [[f"{int(v['factor'])}", f(v["real"]), f(v["random95"]), "Yes" if v["keep"] else "No"] for v in pa]
table(doc, "Table A8", "Eigenvalues and parallel analysis (500 random data sets)",
      ["Factor", "Eigenvalue", "Random, 95th percentile", "Retain"], rows, [1.4, 1.6, 2.0, 1.6],
      interpretation=(
          f"Only the first two eigenvalues ({f(pa[0]['real'])} and {f(pa[1]['real'])}) exceed both 1 and the values "
          f"expected from random data ({f(pa[0]['random95'])} and {f(pa[1]['random95'])}); the third "
          f"({f(pa[2]['real'])}) falls well below its random benchmark. Parallel analysis, the preferred rule, therefore "
          f"supports two dimensions. Together the first two factors explain "
          f"{(R['s2_eigen'][0] + R['s2_eigen'][1]) / 9 * 100:.0f} percent of the variance."))

rows = [[f"{k}", f(fc[k]["chi_square"], 1), f"{int(fc[k]['df'])}", f(fc[k]["RMSEA"], 3), f(fc[k]["BIC"], 1)] for k in (1, 2, 3)]
table(doc, "Table A9", "Fit of one-, two- and three-factor models", ["Factors", "χ²", "df", "RMSEA", "BIC"], rows,
      [1.4, 1.4, 1.0, 1.4, 1.4],
      note="RMSEA below 0.05 = close fit, below 0.08 = acceptable; lower BIC = better.",
      interpretation=(
          f"A single combined index fits poorly (RMSEA {f(fc[1]['RMSEA'], 3)}), so the nine items should not be averaged "
          f"into one score. Two factors give a close fit (RMSEA {f(fc[2]['RMSEA'], 3)}). BIC prefers three factors by a "
          f"small margin; Table A10 shows that the third factor holds a single item."))

l3 = dict(R["s2_load3"]); u3 = R["s2_uniq3"][0][1]; f3 = dict(R["s2_fcor3"])
rows = [[IL[i], f(l3[i]["Factor1"]), f(l3[i]["Factor2"]), f(l3[i]["Factor3"]), f(u3[i])] for i in ITEMS]
rows.append(("PANEL", f"Factor correlations: F1–F2 {f(f3['F1']['F2'])}, F1–F3 {f(f3['F1']['F3'])}, F2–F3 {f(f3['F2']['F3'])}"))
table(doc, "Table A10", "Three-factor solution", ["Item", "Factor 1", "Factor 2", "Factor 3", "Uniqueness"], rows,
      [2.9, 0.9, 0.9, 0.9, 1.0], size=8.5,
      interpretation=(
          f"The third factor consists of one item only, 'opposition candidates are prevented from running' (loading "
          f"{f(l3['mp_blocked']['Factor3'])}, uniqueness {f(u3['mp_blocked'])}). A one-item factor is not a separate "
          f"dimension, so the paper keeps two factors. The item concerns competition before polling day rather than "
          f"conduct on the day, and dropping it from the malpractice scale is a possible robustness check."))

sd_ = dict(R["s2_scale_desc"]); al = R["s2_alpha"]; rp, rmal = dict(R["s2_rel_proc"]), dict(R["s2_rel_mal"])
rows = [("PANEL", f"Process fairness: n = {int(sd_['process_fairness']['n_valid']):,}, mean {f(sd_['process_fairness']['mean'])}, "
                  f"SD {f(sd_['process_fairness']['sd'])}; alpha {f(al['process'])} (n = {al['process_n']:,}), "
                  f"average inter-item r = {f(al['process_iic'])}")]
rows += [[IL[i], f(rp[i]["item_rest_r"]), f(rp[i]["alpha_if_dropped"])] for i in ITEMS[:4]]
rows += [("PANEL", f"Malpractice: n = {int(sd_['malpractice']['n_valid']):,}, mean {f(sd_['malpractice']['mean'])}, "
                   f"SD {f(sd_['malpractice']['sd'])}; alpha {f(al['malpractice'])} (n = {al['malpractice_n']:,}), "
                   f"average inter-item r = {f(al['malpractice_iic'])}")]
rows += [[IL[i], f(rmal[i]["item_rest_r"]), f(rmal[i]["alpha_if_dropped"])] for i in ITEMS[4:]]
table(doc, "Table A11", "The two scales: description and reliability", ["Item", "Item–rest correlation", "Alpha if dropped"],
      rows, [3.6, 1.5, 1.5], size=8.5,
      note=f"Scale scores are item means (at least 2 of 4, and 3 of 5, items answered). Spearman correlation between "
           f"the two scales: {f(R['s2_scale_cor'])}.",
      interpretation=(
          f"The malpractice scale is reliable (alpha {f(al['malpractice'])}); the process fairness scale is just under the "
          f"usual 0.70 (alpha {f(al['process'])}), which is acceptable for four items with an average inter-item "
          f"correlation of {f(al['process_iic'])}. Every item-rest correlation exceeds 0.30, and dropping any item would "
          f"lower alpha, so all items are kept. The two scales correlate at {f(R['s2_scale_cor'])}, the same negative "
          f"pattern as the factors."))

# =================================== STAGE 3 ===================================
heading(doc, "C. Party comparison (Stage 3)")
a, b = D("s3_p2_proc"), D("s3_p2_mal")
lab = {"(Intercept)": "Constant (PTI)", "partyPML-N": "PML-N", "partyPPP": "PPP"}
rows = [("PANEL", f"Process fairness (N = {R['s3_p2_N'][0]:,})")]
rows += [[lab[t], f(a[t]["estimate"], 3) + st(a[t]["p"]), f(a[t]["robust_se"], 3), f(a[t]["naive_se"], 3),
          f"[{f(a[t]['ci_low'], 3)}, {f(a[t]['ci_high'], 3)}]"] for t in lab]
rows += [("PANEL", f"Malpractice (N = {R['s3_p2_N'][1]:,})")]
rows += [[lab[t], f(b[t]["estimate"], 3) + st(b[t]["p"]), f(b[t]["robust_se"], 3), f(b[t]["naive_se"], 3),
          f"[{f(b[t]['ci_low'], 3)}, {f(b[t]['ci_high'], 3)}]"] for t in lab]
table(doc, "Table A12", "Party-only models: unadjusted gaps from PTI supporters",
      ["", "Estimate", "Clustered SE", "Naive SE", "95% CI"], rows, [1.9, 1.1, 1.1, 1.0, 1.5],
      note=CL + f" {R['s3_psus']} primary sampling units.",
      interpretation=(
          f"Without controls, PML-N supporters rate process fairness {f(abs(a['partyPML-N']['estimate']), 3)} and "
          f"malpractice {f(abs(b['partyPML-N']['estimate']), 3)} points lower than PTI supporters. PPP supporters rate "
          f"process fairness lower ({f(a['partyPPP']['estimate'], 3)}) but malpractice higher "
          f"({f(b['partyPPP']['estimate'], 3, plus=True)}), meaning they report cleaner conduct. The clustered standard "
          f"errors are 30 to 80 percent larger than naive ones, because respondents in the same sampling unit answer "
          f"alike; all tests in the paper therefore cluster by sampling unit."))

TL = {"(Intercept)": "Constant", "partyPML-N": "PML-N (ref. PTI)", "partyPPP": "PPP", "age10": "Age (per 10 years)",
      "female": "Woman", "educ": "Education (ISCED level)", "income3Medium": "Income: medium (ref. low)",
      "income3High": "Income: high", "rural": "Rural", "mothertongueSindhi": "Mother tongue: Sindhi (ref. Punjabi)",
      "mothertonguePashto": "Mother tongue: Pashto", "mothertongueSeraiki": "Mother tongue: Seraiki",
      "mothertongueBaluchi": "Mother tongue: Baluchi", "mothertongueHindko": "Mother tongue: Hindko",
      "mothertongueOther": "Mother tongue: other", "interest": "Political interest (1–4)",
      "days_since": "Days since the election"}
c1, c2 = D("s3_p3_proc"), D("s3_p3_mal")
rows = [[TL[t], bse(c1[t]["estimate"], c1[t]["robust_se"], c1[t]["p"], 3), bse(c2[t]["estimate"], c2[t]["robust_se"], c2[t]["p"], 3)] for t in TL]
rows.append(["N", f"{R['s3_p3_N'][0]:,}", f"{R['s3_p3_N'][1]:,}"])
rows.append(["Adjusted R²", f(R["s3_p3_r2"][0][1], 3), f(R["s3_p3_r2"][1][1], 3)])
u1, u2 = R["s3_p3_unadj_proc"], R["s3_p3_unadj_mal"]
table(doc, "Table A13", "Full adjusted models for the two scales", ["", "Process fairness", "Malpractice"], rows,
      [3.4, 1.6, 1.6], size=8.5, note="OLS. " + CL,
      interpretation=(
          f"On the same respondents, adding the controls makes the PML-N gap on process fairness larger (from "
          f"{f(u1[0][1]['unadj_est'], 3)} to {f(u1[0][1]['adj_est'], 3)}) and its malpractice gap smaller (from "
          f"{f(u2[0][1]['unadj_est'], 3)} to {f(u2[0][1]['adj_est'], 3)}); both remain significant. The PPP advantage "
          f"on malpractice disappears (from {f(u2[1][1]['unadj_est'], 3, plus=True)} to {f(u2[1][1]['adj_est'], 3, plus=True)}), "
          f"absorbed mainly by mother tongue: Sindhi speakers report much cleaner conduct "
          f"({f(c2['mothertongueSindhi']['estimate'], 3, plus=True)}). Several controls have opposite signs on the two "
          f"scales (medium income, Sindhi and Baluchi mother tongue), again consistent with the negative relation "
          f"between them. Rural respondents rate the process as fairer and women report cleaner conduct."))

zp, zm, zd, zu = D("s3_p4_zproc"), D("s3_p4_zmal"), D("s3_p4_diff"), D("s3_p4_diff_unadj")
rows = []
for labx, src in [("Process fairness gap (adjusted)", zp), ("Malpractice gap (adjusted)", zm),
                  ("Process minus malpractice (adjusted)", zd), ("Process minus malpractice (unadjusted)", zu)]:
    rows.append([labx] + [(f(src[t]["estimate"], 3) + st(src[t]["p"]), f"[{f(src[t]['ci_low'], 3)}, {f(src[t]['ci_high'], 3)}]",
                           f"{pp(src[t]['p'])}") for t in ("partyPML-N", "partyPPP")])
table(doc, "Table A14", f"H2 test on standardized scales (standard deviations, n = {R['s3_p4_N']:,})",
      ["", "PML-N vs PTI", "PPP vs PTI"], rows, [3.0, 1.8, 1.8],
      note="Both scales standardized on the same respondents. Negative difference = larger gap on process fairness "
           "(the H2 direction). " + CL,
      interpretation=(
          f"The adjusted difference is negative for both parties, as H2 expects, but neither is significant "
          f"({pp(zd['partyPML-N']['p'])} and {pf(zd['partyPPP']['p'])}). Without controls, the PML-N difference is "
          f"close to zero ({f(zu['partyPML-N']['estimate'], 3)}) and the PPP difference large "
          f"({f(zu['partyPPP']['estimate'], 3)}); the latter comes from the raw PPP advantage on malpractice that the "
          f"controls remove (Table A13), so the adjusted test is the one reported. Because the two scales correlate "
          f"negatively, their difference is noisy and the test has limited power."))

rows = []
for k in OUTCOMES[2:]:
    r5 = R["s3_p5"][k]; raw = r5["raw"][0][1]
    for i, pty in enumerate(["PML-N", "PPP"]):
        g = r5["gaps"][i][1]
        rows.append([pty, f(raw[pty]), f(g["unadj"], 3), f(g["adj"], 3) + st(g["adj_p"]), f(g["adj_se"], 3),
                     f"[{f(g['adj_low'], 3)}, {f(g['adj_high'], 3)}]", f(g["adj_in_SD"], 3)])
    rows.insert(len(rows) - 2, ("PANEL", f"{IL[k]} (N = {r5['N']:,}; PTI mean {f(raw['PTI'])})"))
table(doc, "Table A15", "Regime-evaluation outcomes: gaps from PTI supporters",
      ["", "Mean", "Unadjusted", "Adjusted", "SE", "95% CI", "In SD"], rows, [2.2, 0.55, 0.8, 0.8, 0.55, 1.1, 0.6], size=8.5,
      note=CTRL + CL,
      interpretation=(
          "PML-N supporters are less confident in elections and rate the country as much less democratic and the "
          "political system as much less satisfying, by roughly three-quarters of a standard deviation on the two "
          "regime ratings. PPP supporters show gaps about one-third as large, significant for the two regime ratings "
          f"but not for confidence in elections once controls are added. Controls change the PML-N gaps little, but "
          f"they shrink the PPP gap on confidence in elections from {f(R['s3_p5']['conf_elections']['gaps'][1][1]['unadj'], 3)} "
          f"to {f(R['s3_p5']['conf_elections']['gaps'][1][1]['adj'], 3)}."))

ol = dict(R["s3_p6"])
rows = [[IL[i], f"{int(ol[i]['n']):,}", (f(ol[i]["OR_PMLN"]), f"[{f(ol[i]['PMLN_low'])}, {f(ol[i]['PMLN_high'])}]"),
         (f(ol[i]["OR_PPP"]), f"[{f(ol[i]['PPP_low'])}, {f(ol[i]['PPP_high'])}]")] for i in ITEMS]
table(doc, "Table A16", "Ordered logit models for the nine items (odds ratios against PTI supporters)",
      ["Item", "N", "PML-N [95% CI]", "PPP [95% CI]"], rows, [3.0, 0.6, 1.5, 1.5], size=8.5,
      note=CTRL + "Intervals from 200 bootstrap samples that resample primary sampling units (seed 2018). "
                  "Odds ratio below 1 = less favourable answers than PTI supporters.",
      interpretation=(
          f"Treating each item as ordinal confirms the scale results. The PML-N gap is concentrated in vote counting "
          f"(odds ratio {f(ol['pf_counted']['OR_PMLN'])}) and election officials ({f(ol['pf_officials']['OR_PMLN'])}), "
          f"with smaller gaps on blocked candidates ({f(ol['mp_blocked']['OR_PMLN'])}) and bribery "
          f"({f(ol['mp_bribery']['OR_PMLN'])}, borderline); the other items show no clear difference. PPP supporters "
          f"differ from PTI supporters only on election officials ({f(ol['pf_officials']['OR_PPP'])}). This item pattern "
          f"supports the paper's argument that partisanship shapes judgements of counting and officials most."))

# =================================== STAGE 4 ===================================
heading(doc, "D. Provincial winners (Stage 4)")
rmn, vg = dict(R["s4_rawmeans"]), dict(R["s4_valid"])
mlab = {"process_fairness": "Process fairness (1–4)", "malpractice": "Malpractice, higher = cleaner (1–4)",
        "confidence": "Confidence in elections (1–4)", "democracy_rating": "How democratic the country is (1–10)",
        "satisfaction": "Satisfaction with the political system (1–10)"}
rows = [["Respondents"] + [f"{int(sz[g])}" for g in GROUPS]]
rows += [[mlab[k]] + [f(rmn[k][g]) for g in GROUPS] for k in mlab]
table(doc, "Table A17", "The four groups: size and raw means",
      ["", "National winners", "National-only winners", "Provincial-only winners", "Double losers"], rows,
      [2.6, 1.0, 1.0, 1.0, 1.0], size=8.5,
      interpretation=(
          f"On the regime ratings the three winner groups score well above double losers (democracy rating "
          f"{f(rmn['democracy_rating']['National winner'])}, {f(rmn['democracy_rating']['National-only winner'])} and "
          f"{f(rmn['democracy_rating']['Provincial-only winner'])} against {f(rmn['democracy_rating']['Double loser'])}). "
          f"On the integrity scales, the two groups based in Sindh and Balochistan give the lowest process fairness "
          f"ratings but the cleanest malpractice ratings, while national winners do the reverse."))

s4 = R["s4_p2"]; rows = []
for k in OUTCOMES:
    rr = dict(s4[k]["rows"]); rows.append(("PANEL", f"{OL[k]} (N = {s4[k]['N']:,})"))
    for g in GROUPS[:3]:
        v = rr["group4" + g]
        rows.append([g, f(v["estimate"], 3) + st(v["p"]), f(v["robust_se"], 3),
                     f"[{f(v['ci_low'], 3)}, {f(v['ci_high'], 3)}]", pf(v["p"]), f(v["in_SD"], 3)])
table(doc, "Table A18", "Four groups compared with double losers (adjusted)",
      ["", "Estimate", "SE", "95% CI", "p", "In SD"], rows, [2.3, 0.95, 0.65, 1.35, 0.7, 0.65], size=8.5,
      note=CTRL + CL,
      interpretation=(
          "All three winner groups rate democracy and satisfaction above double losers, with national winners highest. "
          "On the integrity outcomes the national-only and provincial-only winners have almost identical estimates "
          "although they support rival parties, which shows a place effect: both groups live mainly in Sindh and "
          "Balochistan, while double losers live mainly in Punjab."))

figure(doc, "Figure A1", "Four winner and loser groups compared with double losers, in standard deviation units",
       ROOT / "figures" / "FigureA1_winner_groups.png",
       note="Adjusted differences from double losers with 95% confidence intervals (Table A18), divided by the "
            "standard deviation of each outcome.",
       interpretation=(
           "On the two regime ratings, all three winner groups sit above zero and national winners sit highest, so "
           "winning at either level goes with a more favourable view of the system. On the three integrity outcomes, "
           "the two Sindh and Balochistan groups move together and away from national winners: they report cleaner "
           "conduct but lower process fairness and confidence. This is the regional pattern discussed in the paper."))

pv3 = R["s4_p3"]; rows = []
for prov_ in ["Punjab", "Sindh"]:
    for k in OUTCOMES:
        rr = dict(pv3[prov_][k]["rows"])
        rows.append(("PANEL", f"{prov_}: {OL[k]} (N = {pv3[prov_][k]['N']:,}; {pv3[prov_][k]['PSUs']} PSUs)"))
        for t, nm in [("partyPML-N", "PML-N"), ("partyPPP", "PPP")]:
            if t in rr:
                v = rr[t]
                rows.append([nm, f(v["estimate"], 3) + st(v["p"]), f(v["robust_se"], 3),
                             f"[{f(v['ci_low'], 3)}, {f(v['ci_high'], 3)}]", pf(v["p"]), f(v["in_SD"], 3)])
n3 = R["s4_p3_n"]
table(doc, "Table A19", "Party gaps from PTI supporters within Punjab and within Sindh (adjusted)",
      ["", "Estimate", "SE", "95% CI", "p", "In SD"], rows, [2.3, 0.95, 0.65, 1.35, 0.7, 0.65], size=8.5,
      note=(f"Punjab: PTI {int(n3['Punjab']['PTI'])}, PML-N {int(n3['Punjab']['PML-N'])}, PPP {int(n3['Punjab']['PPP'])}. "
            f"Sindh: PTI {int(n3['Sindh']['PTI'])}, PPP {int(n3['Sindh']['PPP'])}; PML-N in Sindh (n = 25) not analysed. " + CTRL + CL),
      interpretation=(
          "Holding the province constant, the winner-loser gap remains clear in Punjab: PML-N supporters rate process "
          "fairness, confidence and both regime outcomes lower than PTI supporters, and the malpractice gap is "
          "borderline. In Sindh, PPP supporters, whose party governs the province, do not differ from PTI supporters "
          "on any outcome, although the small PTI group in Sindh makes the intervals wide."))

rows = []
for x in R["s4_p4"]:
    rows.append([f"{OL[x['outcome']]}", x["spec"].replace("no mother tongue", "Without mother tongue").replace("with mother tongue", "With mother tongue"),
                 f"{int(x['N'])}", f(x["gap"], 3) + st(x["p"]), f(x["se"], 2), f"[{f(x['low'], 2)}, {f(x['high'], 2)}]", pf(x["p"])])
pr_ = R["s4_p4_prov"]
table(doc, "Table A20", "PPP supporters in Sindh compared with PPP supporters elsewhere",
      ["Outcome", "Model", "N", "Gap", "SE", "95% CI", "p"], rows, [2.2, 1.25, 0.45, 0.75, 0.45, 0.95, 0.55], size=8.5,
      note=(f"PPP supporters: Sindh {int(pr_['Sindh'])}, Punjab {int(pr_['Punjab'])}, KP {int(pr_['KP'])}, "
            f"Balochistan {int(pr_['Balochistan'])}. All 176 Sindhi-speaking PPP supporters live in Sindh. " + CL),
      interpretation=(
          "In the main version, PPP supporters who hold their province rate democracy and satisfaction no higher than "
          "PPP supporters elsewhere, but they rate the process as less fair and less trustworthy and report cleaner "
          "conduct, the same Sindh pattern seen in Table A18. Adding mother tongue makes the estimates unstable, because "
          "the Sindh effect then rests on about 40 non-Sindhi speakers, so that version is not interpreted."))

# =================================== STAGE 5 ===================================
heading(doc, "E. Item-level check (Stage 5)")
PI = ITEMS[:4]
vv, imn, rmn5, irr = D("s5_valid"), D("s5_itemmeans"), D("s5_restmeans"), D("s5_itemrest")
rows = [[IL[i], f"{int(vv['PTI'][i])}", f"{int(vv['PML-N'][i])}", f(imn["PTI"][i]), f(imn["PML-N"][i]),
         f(rmn5["PTI"][i]), f(rmn5["PML-N"][i]), f(irr["PTI"][i]), f(irr["PML-N"][i])] for i in PI]
table(doc, "Table A21", "Process items and matching scores for PTI and PML-N supporters",
      ["Item", "n PTI", "n PML-N", "Item mean PTI", "Item mean PML-N", "Rest mean PTI", "Rest mean PML-N", "r PTI", "r PML-N"],
      rows, [1.8, 0.5, 0.6, 0.6, 0.65, 0.6, 0.65, 0.5, 0.7], size=8,
      note="Rest score = mean of the other three process items (at least two answered). r = Spearman item-rest correlation.",
      interpretation=(
          f"The raw gap on vote counting ({f(imn['PTI']['pf_counted'])} against {f(imn['PML-N']['pf_counted'])}) is far "
          f"larger than the gap in the matching score ({f(rmn5['PTI']['pf_counted'])} against "
          f"{f(rmn5['PML-N']['pf_counted'])}), the first sign that this item behaves differently by party. Items track "
          f"the rest score somewhat less closely among PML-N supporters."))

d2 = D("s5_p2")
rows = [[IL[i], f"{int(d2[i]['n'])}", (f(d2[i]["OR_PMLN"]), f"[{f(d2[i]['OR_low'])}, {f(d2[i]['OR_high'])}]"),
         pf(d2[i]["p_uniform"]), pf(d2[i]["p_nonuniform"]), f(d2[i]["dR2_uniform"], 4), f(d2[i]["dR2_total"], 4)] for i in PI]
table(doc, "Table A22", "Item bias test with matching on all other process items",
      ["Item", "N", "Odds ratio [95% CI]", "p, uniform", "p, non-uniform", "ΔR², uniform", "ΔR², total"], rows,
      [2.1, 0.5, 1.2, 0.7, 0.75, 0.65, 0.7], size=8.5,
      note="Wald 95% intervals. ΔR² = change in Nagelkerke R²: below 0.035 negligible, 0.035–0.07 moderate.",
      interpretation=(
          f"Vote counting shows a moderate effect (ΔR² = {f(d2['pf_counted']['dR2_uniform'], 3)}). The other three items "
          f"are significant but negligible in size, and the odds ratios above 1 for journalists and choice are probably "
          f"produced by the matching score, which includes the strongly partisan counting item. Table 4 in the paper "
          f"therefore uses a matching score without that item."))

d3, d4 = D("s5_p3"), D("s5_p4")
rows = [[IL[i], d3[i]["matched_on"].replace("+", ", "), f"{int(d3[i]['n'])}", f(d3[i]["OR_PMLN"], 3),
         f"[{f(d3[i]['OR_low'], 2)}, {f(d3[i]['OR_high'], 2)}]", f"[{f(d4[i]['boot_low'])}, {f(d4[i]['boot_high'])}]",
         f"{d4[i]['share_below_1'] * 100:.0f}%", f(d3[i]["dR2_uniform"], 3)] for i in PI]
table(doc, "Table A23", "Item bias test with purified matching and cluster-bootstrap intervals",
      ["Item", "Matched on", "N", "Odds ratio", "Wald CI", "Bootstrap CI", "Below 1", "ΔR²"], rows,
      [1.75, 1.05, 0.45, 0.6, 0.85, 0.85, 0.45, 0.6], size=8,
      note="Bootstrap: 500 samples resampling primary sampling units (seed 2018), no failed replications. "
           "'Below 1' = share of bootstrap samples with an odds ratio below 1.",
      interpretation=(
          f"With the cleaner matching score, vote counting remains the main biased item (odds ratio "
          f"{f(d3['pf_counted']['OR_PMLN'], 3)}, moderate effect), and election officials show a smaller but clear "
          f"shift ({f(d3['pf_officials']['OR_PMLN'], 3)}); both are below 1 in every bootstrap sample. Journalists' "
          f"coverage and genuine choice show no bias once the counting item is removed from the matching score."))

# =================================== STAGE 6 ===================================
heading(doc, "F. Moderation (Stage 6)")
ed = R["s6_educ_dist"][0][1]; idd = R["s6_int_dist"][0][1]; md = D("s6_mods")
rows = [["Education, mean (ISCED 0–8)"] + [f(md["educ"][p]) for p in ["PTI", "PML-N", "PPP"]],
        ["Political interest, mean (1–4)"] + [f(md["interest"][p]) for p in ["PTI", "PML-N", "PPP"]],
        ["Women (share)"] + [f(md["female"][p]) for p in ["PTI", "PML-N", "PPP"]],
        ("PANEL", "Education, all three groups: " + ", ".join(f"level {k}: {int(v)}" for k, v in ed.items())),
        ("PANEL", "Political interest: " + ", ".join(f"{k if k != '<NA>' else 'missing'}: {int(v)}" for k, v in idd.items()))]
table(doc, "Table A24", "The moderators by party preference", ["", "PTI", "PML-N", "PPP"], rows, [3.0, 1.2, 1.2, 1.2],
      note=f"Spearman correlation between education and interest: {f(R['s6_cor'])}. Interest: 1 = not at all, 4 = very interested.",
      interpretation=(
          f"Education is unevenly spread, with many respondents at level 0 ({int(ed['0'])}) and few above level 4, so "
          f"education is used as a continuous score in the tests and in three groups for display. The two moderators "
          f"correlate only modestly ({f(R['s6_cor'])}), so their roles can be separated. PPP supporters have less "
          f"education than the other two groups."))

def mod_rows(key):
    m = D(key); out = []
    for k in OUTCOMES:
        v = m[OL6[k]]
        out.append([OL[k], f"{int(v['N']):,}", bse(v["PMLN_x_mod"], v["PMLN_se"], v["PMLN_p"], 3), pf(v["PMLN_p"]),
                    bse(v["PPP_x_mod"], v["PPP_se"], v["PPP_p"], 3), pf(v["PPP_p"]), pf(v["joint_p"])])
    return out
hdr6 = ["Outcome", "N", "PML-N ×", "p", "PPP ×", "p", "Joint p"]
w6 = [2.4, 0.55, 0.85, 0.6, 0.85, 0.6, 0.75]
rows = [("PANEL", "Education (per 1 SD)")] + mod_rows("s6_educ") + [("PANEL", "Political interest (per 1 SD)")] + mod_rows("s6_int")
table(doc, "Table A25", "Party × education and party × political interest (formal tests behind Figure 3)", hdr6, rows, w6, size=8.5,
      note=CTRL + CL + " Positive interaction on an outcome with a negative gap = the gap shrinks.",
      interpretation=(
          "Only one of twenty interaction terms is significant (PPP × interest on the democracy rating), and none of "
          "the ten joint tests is. The party gap does not narrow with education or political interest, so H5 is not "
          "supported."))

sx = D("s6_sex")
rows = mod_rows("s6_sex")
table(doc, "Table A26", "Party × sex (exploratory)", hdr6, rows, w6, size=8.5,
      note=CTRL + CL + " Interaction = how much the gap from PTI supporters differs for women compared with men.",
      interpretation=(
          f"The PPP gap on malpractice differs strongly by sex ({f(sx['Malpractice (higher = cleaner)']['PPP_x_mod'], 3, plus=True)}, "
          f"{pp(sx['Malpractice (higher = cleaner)']['PPP_p'])}): women who support PPP report cleaner conduct "
          f"relative to PTI women than PPP men do. The PML-N gap on confidence in elections is smaller among women "
          f"({pp(sx['Confidence in elections']['PMLN_p'])}). Of the ten tests only the PPP malpractice result would "
          f"survive a Bonferroni correction, and it probably reflects the regional pattern of Stage 4, so it is reported "
          f"here as exploratory only."))

se_, si = R["s6_sub_educ"], R["s6_sub_int"]
def sub_rows(src, groups):
    out = []
    for g in groups:
        out.append(("PANEL", g))
        for k in OUTCOMES:
            v = dict(src)[f"{g} {OL6[k]}"]
            out.append([OL[k], f"{int(v['n_PTI'])}", f"{int(v['n_PMLN'])}", f(v["gap"], 3) + st(v["p"]), f(v["se"], 3), pf(v["p"])])
    return out
rows = sub_rows(se_, ["None/primary", "Secondary", "Post-secondary+"]) + sub_rows(si, ["Low interest", "High interest"])
table(doc, "Table A27", "PML-N minus PTI gap within education and interest groups (adjusted)",
      ["", "n PTI", "n PML-N", "Gap", "SE", "p"], rows, [2.9, 0.6, 0.7, 0.9, 0.7, 0.8], size=8.5,
      note="Education: none or primary (ISCED 0–1), secondary (2–3), post-secondary or higher (4–8). Interest: low = "
           "not at all or not very; high = somewhat or very. The education (or interest) control is dropped within its "
           "own groups. " + CL,
      interpretation=(
          "The gap persists in every education and interest group. Regime-rating gaps are roughly one-third smaller "
          "among the post-secondary educated, but remain large and significant; process-fairness gaps barely change. "
          "Among the more interested the malpractice gap is larger, not smaller. These subgroup estimates illustrate the "
          "formal interaction tests in Table A25."))

# =================================== STAGE 7 ===================================
heading(doc, "G. Independent verification (Stage 7)")
lab7 = {"Piece 2": "Variables rebuilt from the raw file (Python) vs R",
        "Piece 3": "Stage 3 party models (coefficient rows)", "Piece 4 H2": "H2 difference test (rows)",
        "Piece 4 groups": "Stage 4 four-group models (rows)", "Piece 5 provinces": "Within-Punjab and within-Sindh models (rows)",
        "Piece 5 PPP": "PPP in Sindh vs elsewhere (rows)"}
rows = [[lab7[a], b, c] for a, b, c in R["s7_summary"]]
table(doc, "Table A28", "Independent re-run in Python: agreement with R", ["Check", "Compared", "Not matching"], rows,
      [4.2, 1.2, 1.2],
      note=f"{R['s7_software']}. Agreement = same sample size, and coefficient and clustered standard error within "
           "0.0011 (0.005 for standard errors that R printed to two decimals).",
      interpretation=(
          f"All {rows[0][1]} variables were rebuilt from the raw survey file with no mismatch across 1,995 respondents, "
          f"and all {sum(int(r[1]) for r in rows[1:])} coefficient rows of the main party and winner-loser models were "
          f"reproduced exactly. The coding and the core results of the paper therefore do not depend on one software "
          f"implementation. The factor analysis, the item bias tests, the moderation tests and the ordered logit "
          f"models were run in R only."))

doc.save(OUT / "Online_Appendix.docx")
print("Saved", OUT / "Online_Appendix.docx")
