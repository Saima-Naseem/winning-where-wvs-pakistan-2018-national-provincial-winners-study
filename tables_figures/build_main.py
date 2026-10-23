"""
Main tables and figures for the paper (Main_Tables_Figures.docx).
Every number comes from results/results.json (parsed from the stage logs).
"""
from pathlib import Path
import json
from docx_helpers import *

ROOT = Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "results" / "results.json").read_text(encoding="utf-8"))
FIG = ROOT / "figures"; OUT = ROOT / "paper"; OUT.mkdir(exist_ok=True)
D = lambda key: dict(R[key])

OUTCOMES = ["scale_process", "scale_malprac", "conf_elections", "democracy_rating", "satisfaction"]
OUT_LAB = {"scale_process": "Process fairness (1–4)", "scale_malprac": "Malpractice, higher = cleaner (1–4)",
           "conf_elections": "Confidence in elections (1–4)",
           "democracy_rating": "How democratic the country is (1–10)",
           "satisfaction": "Satisfaction with the political system (1–10)"}
SHORT = {"scale_process": "Process fairness", "scale_malprac": "Malpractice",
         "conf_elections": "Confidence in elections", "democracy_rating": "Democracy rating",
         "satisfaction": "Satisfaction"}
CTRL_NOTE = ("OLS regression. Controls: age, sex, education, income (three groups), rural residence, "
             "mother tongue, political interest and days between the election and the interview. "
             "Standard errors (in parentheses) are clustered by primary sampling unit (CR1 correction; "
             "t-tests with clusters minus one degrees of freedom). * p < .05, ** p < .01, *** p < .001.")

doc = new_doc("Winning where? National and provincial differences in perceptions of Pakistan's 2018 election",
              "Main tables and figures with interpretation. World Values Survey Wave 7, Pakistan (fieldwork "
              f"4 November to 11 December 2018, N = 1,995). All outcomes are coded so that higher values mean "
              "a more favourable view of the election or the political system.")

# ============================== TABLE 1 ==============================
n = R["s1_party"]; mods = D("s6_mods"); rm = D("s3_rawmeans"); va = D("s3_valid"); m1 = D("s1_means")
P3 = ["PTI", "PML-N", "PPP"]
t1 = [["Respondents (n)"] + [f"{int(n[p]):,}" for p in P3],
      ["Women (%)"] + [f"{mods['female'][p] * 100:.0f}" for p in P3],
      ["Education, mean (ISCED level 0–8)"] + [f(mods["educ"][p]) for p in P3],
      ["Political interest, mean (1–4)"] + [f(mods["interest"][p]) for p in P3],
      ("PANEL", "Outcome means (higher = more favourable)"),
      ["Process fairness (1–4)"] + [(f(rm["process_fairness"][p]), f"n = {int(va['process_fairness'][p])}") for p in P3],
      ["Malpractice, higher = cleaner (1–4)"] + [(f(rm["malpractice"][p]), f"n = {int(va['malpractice'][p])}") for p in P3],
      ["Confidence in elections (1–4)"] + [f(m1[p]["conf_elections"]) for p in P3],
      ["How democratic the country is (1–10)"] + [f(m1[p]["democracy_rating"]) for p in P3],
      ["Satisfaction with the political system (1–10)"] + [f(m1[p]["satisfaction"]) for p in P3]]
gap_dem = m1["PTI"]["democracy_rating"] - m1["PML-N"]["democracy_rating"]
table(doc, "Table 1", "Respondents and outcome means by party preference", ["", "PTI", "PML-N", "PPP"], t1,
      [3.0, 1.2, 1.2, 1.2],
      note=("Party preference is the party the respondent would vote for if an election were held tomorrow. "
            "Means use all valid answers; 'don't know' and 'no answer' are treated as missing. The process "
            "fairness scale is the mean of four items (at least two answered) and the malpractice scale the "
            "mean of five items (at least three answered)."),
      interpretation=(
          f"PTI supporters are the largest group ({int(n['PTI'])}), followed by PML-N ({int(n['PML-N'])}) and PPP "
          f"({int(n['PPP'])}) supporters. The three groups are similar in political interest "
          f"({f(mods['interest']['PTI'])} to {f(mods['interest']['PML-N'])}) and in the share of women "
          f"({mods['female']['PTI'] * 100:.0f} to {mods['female']['PML-N'] * 100:.0f} percent), but PPP supporters "
          f"have less education on average ({f(mods['educ']['PPP'])} against {f(mods['educ']['PTI'])} for PTI). "
          f"Before any controls, PTI supporters give the most favourable ratings on process fairness "
          f"({f(rm['process_fairness']['PTI'])}), confidence in elections and the two regime ratings. The largest raw "
          f"difference is in how democratic the country is seen to be: {f(m1['PTI']['democracy_rating'])} for PTI "
          f"supporters against {f(m1['PML-N']['democracy_rating'])} for PML-N supporters, a gap of "
          f"{f(gap_dem, 1)} points on a ten-point scale. PPP supporters stand out on malpractice, where they report "
          f"cleaner conduct ({f(rm['malpractice']['PPP'])}) than both PTI ({f(rm['malpractice']['PTI'])}) and PML-N "
          f"({f(rm['malpractice']['PML-N'])}) supporters. These are raw differences; Table 2 tests them with controls."))

# ============================== TABLE 2 ==============================
p3, m3 = D("s3_p3_proc"), D("s3_p3_mal"); p5 = R["s3_p5"]
def gap_row(k, i):           # i = 0 PML-N, 1 PPP
    term = ["partyPML-N", "partyPPP"][i]
    if k == "scale_process": v = p3[term]; return bse(v["estimate"], v["robust_se"], v["p"])
    if k == "scale_malprac": v = m3[term]; return bse(v["estimate"], v["robust_se"], v["p"])
    g = p5[k]["gaps"][i][1]; return bse(g["adj"], g["adj_se"], g["adj_p"])
Ns = {"scale_process": R["s3_p3_N"][0], "scale_malprac": R["s3_p3_N"][1],
      **{k: p5[k]["N"] for k in OUTCOMES[2:]}}
zp, zm, zd = D("s3_p4_zproc"), D("s3_p4_zmal"), D("s3_p4_diff")
t2 = [("PANEL", "A. Gap from PTI supporters, adjusted (scale points)")]
t2 += [[OUT_LAB[k], gap_row(k, 0), gap_row(k, 1), f"{Ns[k]:,}"] for k in OUTCOMES]
t2 += [("PANEL", f"B. Test of H2 on standardized scales (standard deviations; same {R['s3_p4_N']:,} respondents)")]
for lab, src in [("Process fairness gap", zp), ("Malpractice gap", zm), ("Process gap minus malpractice gap", zd)]:
    t2.append([lab] + [bse(src[t]["estimate"], src[t]["robust_se"], src[t]["p"]) for t in ("partyPML-N", "partyPPP")]
              + [f"{R['s3_p4_N']:,}"])
dem = p5["democracy_rating"]["gaps"]; sat = p5["satisfaction"]["gaps"]; conf = p5["conf_elections"]["gaps"]
table(doc, "Table 2", "Party gaps in judgements of the 2018 election and the political system (H1 and H2)",
      ["", "PML-N vs PTI", "PPP vs PTI", "N"], t2, [3.2, 1.25, 1.25, 0.9],
      note=CTRL_NOTE + (" In Panel B, both scales are standardized (mean 0, SD 1) on the same respondents. The last row "
                        "models the difference between the two standardized scores; a negative value means the "
                        "party gap is larger for process fairness than for malpractice, as H2 expects."),
      interpretation=(
          f"Panel A supports H1. With controls, PML-N supporters rate process fairness "
          f"{f(abs(p3['partyPML-N']['estimate']))} points lower than PTI supporters, report more malpractice "
          f"({f(m3['partyPML-N']['estimate'])}), have less confidence in elections ({f(conf[0][1]['adj'])}), and rate "
          f"the country as less democratic ({f(dem[0][1]['adj'])}) and the political system less satisfying "
          f"({f(sat[0][1]['adj'])}) on the ten-point scales; all five gaps are statistically significant. PPP "
          f"supporters also rate process fairness lower ({f(p3['partyPPP']['estimate'])}) and give lower democracy "
          f"({f(dem[1][1]['adj'])}) and satisfaction ({f(sat[1][1]['adj'])}) ratings, but they do not differ from PTI "
          f"supporters on malpractice ({f(m3['partyPPP']['estimate'], plus=True)}, {pp(m3['partyPPP']['p'])}) or "
          f"confidence in elections ({pp(conf[1][1]['adj_p'])}). Panel B tests H2. In standard deviation units "
          f"the PML-N gap is larger for process fairness ({f(zp['partyPML-N']['estimate'])}) than for malpractice "
          f"({f(zm['partyPML-N']['estimate'])}), and the same is true for PPP. The difference is in the expected "
          f"direction for both parties but is not statistically significant (PML-N {f(zd['partyPML-N']['estimate'])}, "
          f"{pp(zd['partyPML-N']['p'])}; PPP {f(zd['partyPPP']['estimate'])}, {pp(zd['partyPPP']['p'])}). "
          f"H2 is therefore consistent in direction but not supported statistically."))

# ============================== FIGURE 1 ==============================
fd = json.loads((ROOT / "results" / "figure_data.json").read_text())
figure(doc, "Figure 1", "Party gaps on the five outcomes, in standard deviation units",
       FIG / "Figure1_party_gaps.png",
       note=("Adjusted differences from PTI supporters with 95% confidence intervals (standard errors clustered by "
             "primary sampling unit); controls as in Table 2. Process fairness and malpractice are standardized on "
             f"the same {R['s3_p4_N']:,} respondents (Table 2, Panel B); the other three outcomes are rescaled by "
             "their own standard deviation."),
       interpretation=(
           f"The figure puts the five outcomes on one scale. PML-N supporters are below PTI supporters on every "
           f"outcome, and the gap is largest by far on the two broad regime ratings: about "
           f"{f(abs(fd['fig1']['PML-N'][3][0]), 2)} and {f(abs(fd['fig1']['PML-N'][4][0]), 2)} of a standard deviation "
           f"for how democratic the country is and satisfaction with the political system, against "
           f"{f(abs(fd['fig1']['PML-N'][0][0]), 2)} for process fairness and {f(abs(fd['fig1']['PML-N'][1][0]), 2)} for "
           f"malpractice. Partisanship therefore colours the overall judgement of the system more strongly than it "
           f"colours judgements of specific election practices. PPP supporters sit between the two, and their "
           f"malpractice estimate is the only one above zero."))

# ============================== TABLE 3 ==============================
s4 = R["s4_p2"]; pv = R["s4_p3"]; ppp = [x for x in R["s4_p4"] if x["spec"] == "no mother tongue"]
pppd = {x["outcome"]: x for x in ppp}
def g4(k, g):
    v = dict(s4[k]["rows"])["group4" + g]; return bse(v["estimate"], v["robust_se"], v["p"])
def pr(prov, k, term):
    v = dict(pv[prov][k]["rows"])[term]; return bse(v["estimate"], v["robust_se"], v["p"])
hdr = [""] + [SHORT[k] for k in OUTCOMES]
t3 = [("PANEL", "A. Four winner and loser groups, difference from double losers")]
t3 += [[lab] + [g4(k, g) for k in OUTCOMES] for lab, g in
       [("National winners (PTI, Punjab and KP)", "National winner"),
        ("National-only winners (PTI, Sindh and Balochistan)", "National-only winner"),
        ("Provincial-only winners (PPP, Sindh)", "Provincial-only winner")]]
t3.append(["N"] + [f"{s4[k]['N']:,}" for k in OUTCOMES])
t3 += [("PANEL", "B. Within one province, difference from PTI supporters")]
t3 += [["Punjab: PML-N"] + [pr("Punjab", k, "partyPML-N") for k in OUTCOMES],
       ["Punjab: PPP"] + [pr("Punjab", k, "partyPPP") for k in OUTCOMES],
       ["N (Punjab)"] + [f"{pv['Punjab'][k]['N']:,}" for k in OUTCOMES],
       ["Sindh: PPP"] + [pr("Sindh", k, "partyPPP") for k in OUTCOMES],
       ["N (Sindh)"] + [f"{pv['Sindh'][k]['N']:,}" for k in OUTCOMES]]
t3 += [("PANEL", "C. Same party: PPP supporters in Sindh minus PPP supporters elsewhere")]
t3 += [["PPP in Sindh"] + [bse(pppd[k]["gap"], pppd[k]["se"], pppd[k]["p"]) for k in OUTCOMES],
       ["N"] + [f"{int(pppd[k]['N'])}" for k in OUTCOMES]]
pr_dem = dict(s4["democracy_rating"]["rows"]); pr_sat = dict(s4["satisfaction"]["rows"])
sindh_p = {k: dict(pv["Sindh"][k]["rows"])["partyPPP"]["p"] for k in OUTCOMES}
table(doc, "Table 3", "Winning nationally and winning provincially (H3)", hdr, t3,
      [1.85, 0.95, 0.95, 0.95, 0.95, 0.95], size=8.5,
      note=(CTRL_NOTE + " Double losers are PML-N supporters and PPP supporters outside Sindh. Panel B "
            "drops PML-N in Sindh (n = 25). Panel C leaves out mother tongue, because all Sindhi-speaking PPP "
            "supporters live in Sindh."),
      interpretation=(
          f"Panel A shows that, compared with double losers, all three winner groups rate the country as more "
          f"democratic and the political system as more satisfying. Provincial-only winners, the PPP supporters "
          f"of Sindh whose party lost nationally, score {f(pr_dem['group4Provincial-only winner']['estimate'])} and "
          f"{f(pr_sat['group4Provincial-only winner']['estimate'])} points higher, which is below the national "
          f"winners ({f(pr_dem['group4National winner']['estimate'])} and "
          f"{f(pr_sat['group4National winner']['estimate'])}). This is the pattern H3 expects: winning the province "
          f"offsets part of a national loss. The integrity outcomes do not follow this pattern. National-only and "
          f"provincial-only winners, who support rival parties but both live mainly in Sindh and Balochistan, look "
          f"almost the same, and both report cleaner conduct but less confidence in elections than double losers. "
          f"This points to a difference between provinces, not between winners and losers. Panel B holds the province "
          f"constant. In Punjab the PML-N gap is large on almost every outcome, while in Sindh PPP supporters do not "
          f"differ from PTI supporters on any outcome (all p ≥ {pf(min(sindh_p.values()))}). Panel C compares PPP "
          f"supporters with each other: those in Sindh rate democracy and satisfaction no higher than those elsewhere "
          f"({f(pppd['democracy_rating']['gap'], plus=True)} and {f(pppd['satisfaction']['gap'], plus=True)}), "
          f"although this estimate rests on few PPP supporters outside Sindh. H3 is partly supported, for the "
          f"regime ratings only."))

# ============================== TABLE 4 ==============================
im = D("s5_itemmeans"); d3 = D("s5_p3"); d4 = D("s5_p4"); vn = D("s5_valid")
ITEMS = ["pf_counted", "pf_journalists", "pf_officials", "pf_choice"]
ITEM_LAB = {"pf_counted": "Votes are counted fairly", "pf_journalists": "Journalists provide fair coverage",
            "pf_officials": "Election officials are fair", "pf_choice": "Voters are offered a genuine choice"}
size_lab = lambda r2: "Negligible" if r2 < 0.035 else "Moderate" if r2 < 0.07 else "Large"
t4 = [[ITEM_LAB[i], f(im["PTI"][i]), f(im["PML-N"][i]),
       (f(d4[i]["OR_PMLN"]), f"[{f(d4[i]['boot_low'])}, {f(d4[i]['boot_high'])}]"),
       pf(d3[i]["p_uniform"]), pf(d3[i]["p_nonuniform"]), f(d3[i]["dR2_uniform"], 3), size_lab(d3[i]["dR2_uniform"])]
      for i in ITEMS]
table(doc, "Table 4", "Do PTI and PML-N supporters answer the process-fairness items in the same way? (H4)",
      ["Item", "Mean PTI", "Mean PML-N", "Odds ratio [95% CI]", "p, uniform", "p, non-uniform", "ΔR²", "Size"], t4,
      [1.75, 0.6, 0.65, 0.95, 0.6, 0.7, 0.5, 0.85], size=8.5,
      note=("Ordinal logistic regression test of differential item functioning, PML-N against PTI supporters "
            f"(n = {int(min(d3[i]['n'] for i in ITEMS))}–{int(max(d3[i]['n'] for i in ITEMS))} per item, both groups "
            "together). "
            "Each item is predicted from the respondent's mean score on the other process items (vote counting is "
            "left out of the matching score for the other three items), then party, then the interaction of party and matching score. "
            "The odds ratio compares PML-N with PTI supporters at the same matching score; its interval comes from "
            "500 bootstrap samples that resample whole primary sampling units. ΔR² is the change in Nagelkerke "
            "R² when party is added: below 0.035 negligible, 0.035–0.07 moderate, above 0.07 large."),
      interpretation=(
          f"The vote-counting item is answered differently by the two groups. At the same rating of the other "
          f"aspects of the election, PML-N supporters have {round((1 - d4['pf_counted']['OR_PMLN']) * 100)} percent "
          f"lower odds of a favourable answer (odds ratio {f(d4['pf_counted']['OR_PMLN'])}, interval "
          f"{f(d4['pf_counted']['boot_low'])} to {f(d4['pf_counted']['boot_high'])}), and the effect size is moderate "
          f"(ΔR² = {f(d3['pf_counted']['dR2_uniform'], 3)}). The election-officials item shows a smaller shift "
          f"(odds ratio {f(d4['pf_officials']['OR_PMLN'])}), which is statistically clear but negligible in size "
          f"(ΔR² = {f(d3['pf_officials']['dR2_uniform'], 3)}). Journalists' coverage and genuine choice show no "
          f"difference. None of the items shows non-uniform differences, so where party matters it shifts answers "
          f"by the same amount across the scale. H4 is supported for vote counting and, more weakly, for election "
          f"officials. The test cannot say whether PML-N supporters see the counting differently or read the item "
          f"differently; either way, party support changes the answer to this item beyond a person's general view "
          f"of the election."))

# ============================== FIGURE 2 ==============================
ol = D("s3_p6")
figure(doc, "Figure 2", "Gap between PML-N and PTI supporters on the four process items: overall and at the same "
       "underlying rating", FIG / "Figure2_item_bias.png",
       note=("Circles: odds ratios from ordered logit models with the controls of Table 2. Squares: odds ratios "
             "from the item bias test in Table 4. Intervals from 500 bootstrap samples that resample primary "
             "sampling units. Log scale; 1 means no difference."),
       interpretation=(
           f"For vote counting, most of the overall gap (odds ratio {f(ol['pf_counted']['OR_PMLN'])}) remains when "
           f"PML-N and PTI supporters are compared at the same rating of the other process items "
           f"({f(d4['pf_counted']['OR_PMLN'])}). The partisan difference on this item is thus largely specific to "
           f"the item and is not explained by a general view of the election. The same holds, more weakly, for "
           f"election officials. For journalists' coverage and genuine choice, neither marker is clearly different "
           f"from 1. This item pattern also explains why the scale-level H2 test in Table 2 is weak: the process "
           f"scale averages two strongly partisan items with two that are not."))

# ======================= H5: values for the Figure 3 note =======================
ed, it = D("s6_educ"), D("s6_int")
OL6 = ["Process fairness", "Malpractice (higher = cleaner)", "Confidence in elections",
       "How democratic the country is", "Satisfaction with political system"]
joint_e = [ed[l]["joint_p"] for l in OL6]; joint_i = [it[l]["joint_p"] for l in OL6]
n_sig = sum(1 for src in (ed, it) for l in OL6 for k in ("PMLN_p", "PPP_p") if src[l][k] < 0.05)
dem_i = it["How democratic the country is"]

# ============================== FIGURE 3 ==============================
se_ = D("s6_sub_educ"); si = D("s6_sub_int")
figure(doc, "Figure 3", "The PML-N–PTI gap within education and political interest groups (H5)",
       FIG / "Figure3_moderation.png", width=6.4,
       note=("Adjusted PML-N minus PTI differences estimated separately in each group, with approximate 95% "
             "intervals (estimate ± 1.96 clustered standard errors). Education: none or primary (ISCED 0–1), "
             "secondary (2–3), post-secondary or higher (4–8). Interest: not at all or not very interested (low), "
             "somewhat or very interested (high). Formal tests (full sample, controls as in Table 2, education and "
             "interest standardized, party gaps of PML-N and PPP interacted with each moderator): joint tests of the "
             f"two party interactions, education p = {pf(min(joint_e))} to {pf(max(joint_e))}, political interest "
             f"p = {pf(min(joint_i))} to {pf(max(joint_i))} across the five outcomes; {n_sig} of 20 interaction "
             f"terms significant at p < .05 (PPP with interest on the democracy rating, {f(dem_i['PPP_x_mod'])} per "
             f"standard deviation, {pp(dem_i['PPP_p'])})."),
       interpretation=(
           f"The gap between PML-N and PTI supporters remains in every group. On the democracy rating it is somewhat "
           f"smaller among the post-secondary educated ({f(se_['Post-secondary+ How democratic the country is']['gap'])}) "
           f"than among those with no or primary education ({f(se_['None/primary How democratic the country is']['gap'])}), "
           f"but the intervals overlap and the formal interaction test is not significant (see note). Low and highly interested "
           f"respondents show almost the same gap ({f(si['Low interest How democratic the country is']['gap'])} and "
           f"{f(si['High interest How democratic the country is']['gap'])}). Partisan differences in judging the "
           f"election are therefore not confined to the less educated or the less politically engaged, and H5 is not "
           f"supported: across both moderators only {n_sig} of 20 interaction terms is significant, about what chance "
           f"would produce."))

para(doc, "Software note: data preparation and analysis were carried out in R 4.6.1 (base R, readxl, dplyr, MASS), "
          "and the main party-gap and winner-loser models were independently reproduced in Python 3.14 (pandas, "
          "statsmodels).", size=9.5, italic=True, before=10)
doc.save(OUT / "Main_Tables_Figures.docx")
print("Saved", OUT / "Main_Tables_Figures.docx", "| significant interaction terms:", n_sig)
