# =============================================================================
# STAGE 5: Item-level check (H4) - differential item functioning, PTI vs PML-N
# Paper:  Winning where? National and provincial differences in perceptions
#         of Pakistan's 2018 election
# Input:  stage2_clean.csv (from Stage 2)
# Output: stage5_log.txt (console log)
# Run in: RStudio, piece by piece. Edit only the SETTINGS block.
# =============================================================================

# ---- 0. SETTINGS (edit only this block) --------------------------------------
PROJECT_DIR <- "."   # the repository folder (opening winning-where.Rproj sets it)

# ---- 1. SETUP -----------------------------------------------------------------
while (sink.number() > 0) sink()                      # close any log left open earlier
setwd(PROJECT_DIR)
options(width = 200)
sink("logs/stage5_log.txt", split = TRUE, append = TRUE)

# ---- PIECE 1: sample and matching (rest) scores ---------------------------------------
cat("\n===== STAGE 5, PIECE 1: sample and matching scores =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Load data; keep PTI and PML-N supporters only (H4 compares these two)
d  <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
d5 <- d[d$party %in% c("PTI", "PML-N"), ]
d5$pml <- as.numeric(d5$party == "PML-N")             # 1 = PML-N, 0 = PTI (reference)
rownames(d5) <- NULL
cat("\nRespondents:\n"); print(table(d5$party))

# 2. The four process-fairness items (higher = fairer)
items <- c("pf_counted", "pf_journalists", "pf_officials", "pf_choice")

# 3. Rest score for each item = mean of the OTHER three items (needs at least 2 of the 3)
for (it in items) {
  others <- setdiff(items, it)
  ans    <- rowSums(!is.na(d5[, others]))
  d5[[paste0("rest_", it)]] <- ifelse(ans >= 2, rowMeans(d5[, others], na.rm = TRUE), NA)
}

# 4. Valid cases per item and group (item answered AND rest score available)
cat("\nValid cases (item and rest score present):\n")
print(sapply(items, function(it) {
  ok <- !is.na(d5[[it]]) & !is.na(d5[[paste0("rest_", it)]])
  tapply(ok, d5$party, sum) }))

# 5. Item means and rest-score means by group (description only, not a test)
cat("\nItem means by party:\n")
print(round(sapply(items, function(it) tapply(d5[[it]], d5$party, mean, na.rm = TRUE)), 2))
cat("\nRest-score means by party:\n")
print(round(sapply(items, function(it)
  tapply(d5[[paste0("rest_", it)]], d5$party, mean, na.rm = TRUE)), 2))

# 6. How strongly each item tracks its rest score, within each party (Spearman)
cat("\nItem-rest correlation within party (Spearman):\n")
print(round(sapply(items, function(it) sapply(c("PTI", "PML-N"), function(p) {
  s <- d5[d5$party == p, ]
  cor(s[[it]], s[[paste0("rest_", it)]], method = "spearman", use = "complete.obs") })), 2))

sink()




# ---- PIECE 2: ordinal logistic DIF tests (PTI vs PML-N) ------------------------------
while (sink.number() > 0) sink()
sink("logs/stage5_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 5, PIECE 2: ordinal logistic DIF tests =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d5"), exists("items"))
library(MASS)                                       # pre-installed; provides polr()

# Nagelkerke pseudo-R2 for an ordinal logit, from model deviance vs the intercept-only model
nagelkerke <- function(m, dev_null, n) {
  cs <- 1 - exp((m$deviance - dev_null) / n)        # Cox-Snell
  cs / (1 - exp(-dev_null / n))                     # rescaled so the maximum is 1
}

res <- NULL
for (it in items) {
  rest <- paste0("rest_", it)
  dat  <- d5[complete.cases(d5[, c(it, rest, "pml")]), ]
  dat$y <- factor(dat[[it]], ordered = TRUE)
  dat$r <- dat[[rest]]
  n <- nrow(dat)
  
  m0 <- polr(y ~ 1,         data = dat, method = "logistic")
  m1 <- polr(y ~ r,         data = dat, method = "logistic")
  m2 <- polr(y ~ r + pml,   data = dat, method = "logistic", Hess = TRUE)
  m3 <- polr(y ~ r * pml,   data = dat, method = "logistic")
  
  lr_unif <- m1$deviance - m2$deviance              # uniform DIF (1 df)
  lr_non  <- m2$deviance - m3$deviance              # non-uniform DIF (1 df)
  cf  <- summary(m2)$coefficients["pml", ]
  or  <- exp(cf["Value"])
  ci  <- exp(cf["Value"] + c(-1, 1) * 1.96 * cf["Std. Error"])
  
  res <- rbind(res, data.frame(
    item = it, n = n,
    OR_PMLN = or, OR_low = ci[1], OR_high = ci[2],           # PML-N vs PTI at the same rest score
    p_uniform = pchisq(lr_unif, 1, lower.tail = FALSE),
    p_nonuniform = pchisq(lr_non, 1, lower.tail = FALSE),
    dR2_uniform = nagelkerke(m2, m0$deviance, n) - nagelkerke(m1, m0$deviance, n),
    dR2_total   = nagelkerke(m3, m0$deviance, n) - nagelkerke(m1, m0$deviance, n)))
}
rownames(res) <- NULL
cat("\nOR < 1 = PML-N supporters answer lower than PTI supporters with the same rest score.\n")
cat("Effect size (change in Nagelkerke R2): <0.035 negligible, 0.035-0.07 moderate, >0.07 large.\n\n")
print(format(res, digits = 2, nsmall = 3), row.names = FALSE)

sink()




# ---- PIECE 3: DIF tests with purified matching (vote counting excluded as anchor) ----
while (sink.number() > 0) sink()
sink("logs/stage5_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 5, PIECE 3: DIF with purified matching =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d5"), exists("items"), exists("nagelkerke"))
library(MASS)

# Anchor items (the matching score) for each studied item
anchors <- list(pf_counted     = c("pf_journalists", "pf_officials", "pf_choice"),
                pf_journalists = c("pf_officials", "pf_choice"),
                pf_officials   = c("pf_journalists", "pf_choice"),
                pf_choice      = c("pf_journalists", "pf_officials"))

res <- NULL
for (it in items) {
  a   <- anchors[[it]]
  dat <- d5
  dat$r <- ifelse(rowSums(!is.na(dat[, a])) == length(a), rowMeans(dat[, a]), NA)  # all anchors answered
  dat <- dat[complete.cases(dat[, c(it, "r", "pml")]), ]
  dat$y <- factor(dat[[it]], ordered = TRUE)
  n <- nrow(dat)
  
  m0 <- polr(y ~ 1,       data = dat, method = "logistic")
  m1 <- polr(y ~ r,       data = dat, method = "logistic")
  m2 <- polr(y ~ r + pml, data = dat, method = "logistic", Hess = TRUE)
  m3 <- polr(y ~ r * pml, data = dat, method = "logistic")
  
  cf <- summary(m2)$coefficients["pml", ]
  ci <- exp(cf["Value"] + c(-1, 1) * 1.96 * cf["Std. Error"])
  res <- rbind(res, data.frame(
    item = it, matched_on = paste(sub("pf_", "", a), collapse = "+"), n = n,
    OR_PMLN = exp(cf["Value"]), OR_low = ci[1], OR_high = ci[2],
    p_uniform    = pchisq(m1$deviance - m2$deviance, 1, lower.tail = FALSE),
    p_nonuniform = pchisq(m2$deviance - m3$deviance, 1, lower.tail = FALSE),
    dR2_uniform  = nagelkerke(m2, m0$deviance, n) - nagelkerke(m1, m0$deviance, n)))
}
rownames(res) <- NULL
cat("\nOR < 1 = PML-N supporters answer lower than PTI supporters with the same matching score.\n")
cat("Effect size (change in Nagelkerke R2): <0.035 negligible, 0.035-0.07 moderate, >0.07 large.\n\n")
print(format(res, digits = 2, nsmall = 3), row.names = FALSE)

sink()




# ---- PIECE 4: cluster-bootstrap CIs for the DIF odds ratios --------------------------
while (sink.number() > 0) sink()
sink("logs/stage5_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 5, PIECE 4: cluster-bootstrap CIs for DIF odds ratios =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d5"), exists("items"), exists("anchors"))
library(MASS)
B <- 500                                             # bootstrap replications
set.seed(2018)

# Party odds ratio (PML-N vs PTI) at the same matching score
dif_or <- function(dat) {
  dat$y <- factor(dat$y_raw, ordered = TRUE)
  exp(coef(polr(y ~ r + pml, data = dat, method = "logistic"))["pml"])
}

out <- NULL
for (it in items) {
  a   <- anchors[[it]]
  dat <- d5
  dat$r     <- ifelse(rowSums(!is.na(dat[, a])) == length(a), rowMeans(dat[, a]), NA)
  dat$y_raw <- dat[[it]]
  dat <- dat[complete.cases(dat[, c("y_raw", "r", "pml")]), ]
  
  est  <- dif_or(dat)
  rows <- split(seq_len(nrow(dat)), dat$I_PSU)       # row numbers for each PSU
  boot <- replicate(B, {
    pick <- sample(names(rows), length(rows), replace = TRUE)   # resample whole PSUs
    tryCatch(dif_or(dat[unlist(rows[pick]), ]), error = function(e) NA)
  })
  ci <- quantile(boot, c(0.025, 0.975), na.rm = TRUE)
  out <- rbind(out, data.frame(item = it, n = nrow(dat), OR_PMLN = est,
                               boot_low = ci[1], boot_high = ci[2],
                               share_below_1 = mean(boot < 1, na.rm = TRUE),
                               failed = sum(is.na(boot))))
}
rownames(out) <- NULL
cat("\nPML-N vs PTI odds ratio, purified matching; 95% PSU-cluster-bootstrap interval:\n\n")
print(format(out, digits = 2, nsmall = 2), row.names = FALSE)

sink()




