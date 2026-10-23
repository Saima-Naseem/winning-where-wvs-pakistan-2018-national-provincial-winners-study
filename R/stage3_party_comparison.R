# =============================================================================
# STAGE 3: Party comparison (H1 and H2)
# Paper:  Winning where? National and provincial differences in perceptions
#         of Pakistan's 2018 election
# Input:  stage2_clean.csv (from Stage 2)
# Output: stage3_log.txt (console log)
# Run in: RStudio, piece by piece. Edit only the SETTINGS block.
# =============================================================================

# ---- 0. SETTINGS (edit only this block) --------------------------------------
PROJECT_DIR <- "."   # the repository folder (opening winning-where.Rproj sets it)

# ---- 1. SETUP -----------------------------------------------------------------
setwd(PROJECT_DIR)
options(width = 200)                                # wider console, tables do not wrap
sink("logs/stage3_log.txt", split = TRUE, append = TRUE) # print to console AND save to log

# ---- PIECE 1: load data, define the comparison sample, raw party means -------------
cat("\n===== STAGE 3, PIECE 1: sample and raw party means =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Load the Stage 2 file
d <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
cat("\nRows loaded:", nrow(d), "| Columns:", ncol(d), "\n")

# 2. Check that the packages Stage 3 may need are already installed (nothing is installed here)
pkgs <- c("sandwich", "lmtest", "MASS")
cat("\nPackage availability (TRUE = installed):\n")
print(sapply(pkgs, function(p) p %in% rownames(installed.packages())))

# 3. Comparison sample: respondents who prefer PTI, PML-N or PPP
d3 <- d[d$party %in% c("PTI", "PML-N", "PPP"), ]
d3$party <- factor(d3$party, levels = c("PTI", "PML-N", "PPP"))   # PTI = reference group
cat("\nRespondents by party (comparison sample):\n")
print(table(d3$party))

# 4. Valid answers on each scale within this sample
cat("\nValid scale scores by party:\n")
print(rbind(
  process_fairness = tapply(!is.na(d3$scale_process), d3$party, sum),
  malpractice      = tapply(!is.na(d3$scale_malprac),  d3$party, sum)))

# 5. Raw means by party (higher = fairer / cleaner election). Description only, not a test.
cat("\nRaw scale means by party:\n")
print(round(rbind(
  process_fairness = tapply(d3$scale_process, d3$party, mean, na.rm = TRUE),
  malpractice      = tapply(d3$scale_malprac,  d3$party, mean, na.rm = TRUE)), 2))

sink()                                              # closes stage3_log.txt (re-run line 1 sink for next piece)




# ---- PIECE 2: cluster-robust SE helper + party-only models --------------------------
sink("logs/stage3_log.txt", split = TRUE, append = TRUE)   # re-open the log (Piece 1 closed it)
cat("\n===== STAGE 3, PIECE 2: party-only models, cluster-robust SEs =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Reload data and rebuild the comparison sample (so this piece runs on its own)
d  <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
d3 <- d[d$party %in% c("PTI", "PML-N", "PPP"), ]
d3$party <- factor(d3$party, levels = c("PTI", "PML-N", "PPP"))   # PTI = reference
rownames(d3) <- NULL

# 2. Helper: OLS coefficients with standard errors clustered by PSU
#    Same estimator as sandwich::vcovCL (type "HC1"): CR1 small-sample correction,
#    t-tests with (number of clusters - 1) degrees of freedom.
cluster_robust <- function(model, cluster) {
  X  <- model.matrix(model)
  u  <- residuals(model)
  cl <- cluster[match(rownames(X), rownames(d3))]    # PSU of each row used in the model
  
  
  
  
  # ---- PIECE 3: party models with controls --------------------------------------------
  sink("logs/stage3_log.txt", split = TRUE, append = TRUE)
  cat("\n===== STAGE 3, PIECE 3: party models with controls =====\n")
  cat("Run time:", format(Sys.time()), "\n")
  
  # 0. This piece reuses objects from Piece 2; stop with a clear message if they are missing
  stopifnot(exists("d3"), exists("cluster_robust"))
  
  # 1. Prepare controls (reference categories chosen so coefficients are easy to read)
  d3$income3      <- factor(d3$income3, levels = c("Low", "Medium", "High"))
  d3$mothertongue <- factor(d3$mothertongue,
                            levels = c("Punjabi", "Sindhi", "Pashto", "Seraiki",
                                       "Baluchi", "Hindko", "Other"))
  d3$age10        <- d3$age / 10          # age in decades, so the coefficient is per 10 years
  controls <- c("age10", "female", "educ", "income3", "rural", "mothertongue",
                "interest", "days_since")
  
  # 2. For one outcome: fit unadjusted and adjusted models on the SAME respondents
  run_pair <- function(outcome, label) {
    vars <- c(outcome, "party", controls)
    keep <- complete.cases(d3[, vars])                   # respondents with no missing values
    dat  <- d3[keep, ]                                   # row names kept so the SE helper can match PSUs
    m0 <- lm(reformulate("party", outcome), data = dat)
    m1 <- lm(reformulate(c("party", controls), outcome), data = dat)
    cat("\n=====", label, "=====\n")
    cat("Respondents in model:", nrow(dat), "of", sum(!is.na(d3[[outcome]])),
        "with a valid outcome\n")
    cat("Adjusted R-squared, unadjusted vs adjusted:",
        round(summary(m0)$adj.r.squared, 3), "vs", round(summary(m1)$adj.r.squared, 3), "\n")
    r0 <- cluster_robust(m0, d3$I_PSU)
    r1 <- cluster_robust(m1, d3$I_PSU)
    cat("\nParty coefficients, unadjusted vs adjusted (same respondents):\n")
    print(round(cbind(
      unadj_est = r0[2:3, "estimate"], unadj_se = r0[2:3, "robust_se"],
      adj_est   = r1[2:3, "estimate"], adj_se   = r1[2:3, "robust_se"],
      adj_low   = r1[2:3, "ci_low"],   adj_high = r1[2:3, "ci_high"],
      adj_p     = r1[2:3, "p"]), 3))
    cat("\nFull adjusted model:\n")
    print(round(r1[, c("estimate", "robust_se", "ci_low", "ci_high", "p")], 3))
    invisible(list(m0 = m0, m1 = m1, dat = dat))
  }
  
  res_proc <- run_pair("scale_process", "PROCESS FAIRNESS")
  res_mal  <- run_pair("scale_malprac", "MALPRACTICE")
  
  sink()
  N  <- nrow(X); k <- ncol(X); G <- length(unique(cl))
  bread <- solve(crossprod(X))                       # (X'X)^-1
  Xu    <- rowsum(X * u, group = cl)                 # sum of x*u within each PSU
  meat  <- crossprod(Xu)                             # sum over PSUs of (X_g'u_g)(X_g'u_g)'
  V     <- bread %*% meat %*% bread * (G / (G - 1)) * ((N - 1) / (N - k))
  b     <- coef(model); se <- sqrt(diag(V)); tval <- b / se
  p     <- 2 * pt(abs(tval), df = G - 1, lower.tail = FALSE)
  out <- data.frame(estimate = b, robust_se = se,
                    ci_low = b - qt(0.975, G - 1) * se,
                    ci_high = b + qt(0.975, G - 1) * se,
                    t = tval, p = p,
                    naive_se = summary(model)$coefficients[, "Std. Error"])
  attr(out, "info") <- c(N = N, clusters = G)
  out
}

# 3. Party-only models for the two scales
m_proc <- lm(scale_process ~ party, data = d3)
m_mal  <- lm(scale_malprac ~ party, data = d3)

show <- function(m, label) {
  res <- cluster_robust(m, d3$I_PSU)
  cat("\n---", label, "| N =", attr(res, "info")["N"],
      "| PSUs =", attr(res, "info")["clusters"], "---\n")
  print(round(res, 3))
}
show(m_proc, "Process fairness ~ party")
show(m_mal,  "Malpractice ~ party")

sink()                                                # closes stage3_log.txt




# ---- PIECE 4: H2 test - process gap vs malpractice gap (standardized) ----------------
sink("logs/stage3_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 3, PIECE 4: H2 test on standardized scales =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d3"), exists("controls"), exists("cluster_robust"))

# 1. Same respondents for everything: both scales valid and all controls present
vars <- c("scale_process", "scale_malprac", "party", controls)
dat  <- d3[complete.cases(d3[, vars]), ]            # row names kept for the SE helper
cat("\nRespondents with both scales and all controls:", nrow(dat), "\n")

# 2. Standardize each scale within this sample (mean 0, SD 1); higher = fairer / cleaner
dat$z_proc <- as.numeric(scale(dat$scale_process))
dat$z_mal  <- as.numeric(scale(dat$scale_malprac))
dat$z_diff <- dat$z_proc - dat$z_mal                # party coefficient = process gap minus malpractice gap

# 3. Adjusted models (party + controls) for the three outcomes
fit_adj <- function(outcome) lm(reformulate(c("party", controls), outcome), data = dat)
rows <- function(m) cluster_robust(m, d3$I_PSU)[2:3, c("estimate", "robust_se", "ci_low", "ci_high", "p")]

cat("\n--- Adjusted gap vs PTI, process fairness (SD units) ---\n");  print(round(rows(fit_adj("z_proc")), 3))
cat("\n--- Adjusted gap vs PTI, malpractice (SD units) ---\n");       print(round(rows(fit_adj("z_mal")), 3))
cat("\n--- H2 TEST: process gap minus malpractice gap (adjusted) ---\n")
cat("Positive = malpractice gap is larger (more negative) than the process gap\n")
print(round(rows(fit_adj("z_diff")), 3))

# 4. Same H2 test without controls, for comparison
m_diff0 <- lm(z_diff ~ party, data = dat)
cat("\n--- H2 TEST, unadjusted ---\n")
print(round(cluster_robust(m_diff0, d3$I_PSU)[2:3, c("estimate", "robust_se", "ci_low", "ci_high", "p")], 3))

sink()




# ---- PIECE 5: regime-evaluation outcomes by party ------------------------------------
sink("logs/stage3_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 3, PIECE 5: regime evaluation outcomes =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d3"), exists("controls"), exists("cluster_robust"))

regime <- c(conf_elections   = "Confidence in elections (1-4)",
            democracy_rating = "How democratic the country is (1-10)",
            satisfaction     = "Satisfaction with political system (1-10)")

for (y in names(regime)) {
  keep <- complete.cases(d3[, c(y, "party", controls)])
  dat  <- d3[keep, ]                                  # row names kept for the SE helper
  sdy  <- sd(dat[[y]])                                # outcome SD, to express gaps in SD units
  
  cat("\n=====", regime[y], "| N =", nrow(dat), "=====\n")
  cat("Raw means by party:\n")
  print(round(tapply(dat[[y]], dat$party, mean), 2))
  
  m0 <- lm(reformulate("party", y), data = dat)                      # unadjusted
  m1 <- lm(reformulate(c("party", controls), y), data = dat)         # adjusted
  r0 <- cluster_robust(m0, d3$I_PSU)[2:3, ]
  r1 <- cluster_robust(m1, d3$I_PSU)[2:3, ]
  
  cat("\nGap vs PTI (scale points), unadjusted and adjusted:\n")
  print(round(cbind(unadj = r0$estimate,
                    adj = r1$estimate, adj_se = r1$robust_se,
                    adj_low = r1$ci_low, adj_high = r1$ci_high, adj_p = r1$p,
                    adj_in_SD = r1$estimate / sdy), 3), row.names = TRUE)
  rownames(r1) <- NULL
}

sink()




# ---- PIECE 6: ordered logit on single items, cluster-bootstrap CIs -------------------
sink("logs/stage3_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 3, PIECE 6: ordered logit robustness (9 items) =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d3"), exists("controls"))
library(MASS)                                   # pre-installed; provides polr()

items <- c("pf_counted", "pf_journalists", "pf_officials", "pf_choice",       # process fairness
           "mp_blocked", "mp_tvbias", "mp_bribery", "mp_richbuy", "mp_violence") # malpractice
B <- 200                                        # bootstrap replications
set.seed(2018)

# Fit an ordered logit and return the two party log-odds (vs PTI)
fit_polr <- function(dat, y) {
  dat$yy <- factor(dat[[y]], ordered = TRUE)
  m <- polr(reformulate(c("party", controls), "yy"), data = dat, method = "logistic")
  coef(m)[c("partyPML-N", "partyPPP")]
}

out <- NULL
for (y in items) {
  dat  <- d3[complete.cases(d3[, c(y, "party", controls)]), ]
  est  <- fit_polr(dat, y)
  rows <- split(seq_len(nrow(dat)), dat$I_PSU)             # row numbers for each PSU
  boot <- t(replicate(B, {
    pick <- sample(names(rows), length(rows), replace = TRUE)   # resample whole PSUs
    tryCatch(fit_polr(dat[unlist(rows[pick]), ], y), error = function(e) c(NA, NA))
  }))
  ci <- apply(boot, 2, quantile, probs = c(0.025, 0.975), na.rm = TRUE)
  out <- rbind(out, data.frame(
    item = y, n = nrow(dat),
    OR_PMLN = exp(est[1]), PMLN_low = exp(ci[1, 1]), PMLN_high = exp(ci[2, 1]),
    OR_PPP  = exp(est[2]), PPP_low  = exp(ci[1, 2]), PPP_high  = exp(ci[2, 2])))
}
rownames(out) <- NULL
cat("\nOdds ratios vs PTI (adjusted; 95% cluster-bootstrap CI). OR < 1 = lower ratings than PTI.\n")
print(format(out, digits = 2, nsmall = 2), row.names = FALSE)

sink()

while (sink.number() > 0) sink()
