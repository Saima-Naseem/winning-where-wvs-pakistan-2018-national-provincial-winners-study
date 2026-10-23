# =============================================================================
# STAGE 2: Factor analysis of the nine integrity items
# Paper: Winning where? (WVS-7 Pakistan 2018)
# Input:  stage1_clean.csv (made in Stage 1)
# Output: stage2_log.txt (everything printed below is saved there)
# This script grows piece by piece; each new piece is added at the bottom.
# =============================================================================

# ---- PIECE 1: setup, load the Stage 1 data, look at the nine items -----------
PROJECT_DIR <- "."   # the repository folder (opening winning-where.Rproj sets it)
setwd(PROJECT_DIR)
options(width = 200)                                   # wider console output
sink("logs/stage2_log.txt", split = TRUE, append = TRUE)    # print to console AND log file
cat("\n===== STAGE 2, PIECE 1: look at the nine items =====\n")
cat("Run time:", format(Sys.time()), "\n")

d <- read.csv("data/stage1_clean.csv", stringsAsFactors = FALSE)
stopifnot(nrow(d) == 1995)                             # stop if the wrong file is read

# The nine items; higher always means "more fair / cleaner election"
process_items <- c("pf_counted", "pf_journalists", "pf_officials", "pf_choice")
malprac_items <- c("mp_blocked", "mp_tvbias", "mp_bribery", "mp_richbuy", "mp_violence")
items9 <- c(process_items, malprac_items)

# 1. How many respondents answered all nine items?
cat("\nComplete cases on all nine items:", sum(complete.cases(d[, items9])),
    "of", nrow(d), "\n")

# 2. How were the answers spread (1 = least fair ... 4 = most fair)?
cat("\nAnswer counts per item:\n")
print(sapply(d[, items9], function(x) table(factor(x, levels = 1:4))))

# 3. Spearman correlations (suitable for ordered answers)
cat("\nSpearman correlations among the nine items:\n")
print(round(cor(d[, items9], method = "spearman", use = "pairwise.complete.obs"), 2))


# ---- PIECE 2: is the data suitable for factor analysis? (Bartlett and KMO) ----
cat("\n===== STAGE 2, PIECE 2: suitability check (Bartlett and KMO) =====\n")
cat("Run time:", format(Sys.time()), "\n")

cc <- d[complete.cases(d[, items9]), items9]   # respondents who answered all nine items
n  <- nrow(cc); p <- ncol(cc)
R  <- cor(cc, method = "spearman")             # correlation matrix of the nine items
cat("\nRespondents used:", n, "| Items:", p, "\n")

# Bartlett's test: are the items correlated at all? (small p-value = yes)
bart_chi <- -(n - 1 - (2 * p + 5) / 6) * log(det(R))
bart_df  <- p * (p - 1) / 2
bart_p   <- pchisq(bart_chi, bart_df, lower.tail = FALSE)
cat("\nBartlett's test: chi-square =", round(bart_chi, 1),
    "| df =", bart_df, "| p =", signif(bart_p, 3), "\n")

# KMO: compares ordinary correlations with partial correlations
Rinv    <- solve(R)
partial <- -Rinv / sqrt(outer(diag(Rinv), diag(Rinv)))   # partial correlations
diag(partial) <- 0
R0 <- R; diag(R0) <- 0                                    # correlations without the diagonal
kmo_all  <- sum(R0^2) / (sum(R0^2) + sum(partial^2))
kmo_item <- colSums(R0^2) / (colSums(R0^2) + colSums(partial^2))
cat("\nOverall KMO:", round(kmo_all, 2), "\n")
cat("KMO per item:\n"); print(round(kmo_item, 2))

# Determinant: a value near zero would mean items are almost duplicates
cat("\nDeterminant of the correlation matrix:", signif(det(R), 3),
    "(should be above 0.00001)\n")



# ---- PIECE 3: factor analysis, two factors allowed to correlate ---------------
cat("\n===== STAGE 2, PIECE 3: factor analysis, two factors =====\n")
cat("Run time:", format(Sys.time()), "\n")

cc <- d[complete.cases(d[, items9]), items9]   # the 1,508 complete cases
n  <- nrow(cc)
R  <- cor(cc, method = "spearman")             # correlation matrix of the nine items

# Maximum-likelihood factor analysis, two factors, promax rotation (oblique)
fa2 <- factanal(covmat = R, factors = 2, n.obs = n, rotation = "promax")
cat("\nRespondents:", n, "| maximum likelihood | promax rotation\n")

# 1. Loadings: how strongly each item belongs to each factor
L <- unclass(fa2$loadings)
cat("\nLoadings (rows = items, columns = factors):\n")
print(round(L, 2))

# 2. Correlation between the two factors
Phi <- solve(crossprod(fa2$rotmat))
cat("\nCorrelation between the two factors:", round(Phi[1, 2], 2), "\n")

# 3. Communalities: share of each item's variance explained by the factors
cat("\nCommunalities (higher = better explained):\n")
print(round(1 - fa2$uniquenesses, 2))
cat("Average communality:", round(mean(1 - fa2$uniquenesses), 2), "\n")

# 4. Test of the two-factor model (very sensitive with large samples)
cat("\nTest of the two-factor model: chi-square =", round(fa2$STATISTIC, 1),
    "| df =", fa2$dof, "| p =", signif(fa2$PVAL, 3), "\n")



# ---- PIECE 4: how many dimensions do the data support? -------------------------
cat("\n===== STAGE 2, PIECE 4: how many dimensions? =====\n")
cat("Run time:", format(Sys.time()), "\n")

cc <- d[complete.cases(d[, items9]), items9]   # the 1,508 complete cases
n  <- nrow(cc); p <- ncol(cc)
R  <- cor(cc, method = "spearman")

# 1. Eigenvalues: shared variation captured by each possible factor
ev <- eigen(R)$values
cat("\nEigenvalues:\n"); print(round(ev, 2))
cat("Cumulative share of variance, first two factors:",
    round(cumsum(ev) / p, 2)[1:2], "\n")

# 2. Parallel analysis: keep a factor only if it beats random data
set.seed(2018)                                  # makes the result repeatable
n_rep   <- 500                                  # number of random datasets
rand_ev <- replicate(n_rep, eigen(cor(matrix(rnorm(n * p), n, p)))$values)
pa95    <- apply(rand_ev, 1, quantile, probs = 0.95)   # 95th percentile of random eigenvalues
beats   <- ev > pa95
k_pa    <- ifelse(any(!beats), which(!beats)[1] - 1, p)
cat("\nParallel analysis (real eigenvalue versus 95th percentile of random data):\n")
print(data.frame(factor = 1:p, real = round(ev, 2), random95 = round(pa95, 2),
                 keep = beats), row.names = FALSE)
cat("Number of factors to keep by parallel analysis:", k_pa, "\n")

# 3. Compare models with 1, 2 and 3 factors
fit_tab <- do.call(rbind, lapply(1:3, function(k) {
  f   <- factanal(covmat = R, factors = k, n.obs = n, rotation = "none")
  chi <- f$STATISTIC; df <- f$dof
  data.frame(factors = k, chi_square = round(chi, 1), df = df,
             p_value = signif(f$PVAL, 3),
             RMSEA = round(sqrt(max(chi - df, 0) / (df * (n - 1))), 3),
             BIC = round(chi - df * log(n), 1))
}))
cat("\nComparison of 1, 2 and 3 factors:\n"); print(fit_tab, row.names = FALSE)
cat("\nRules of thumb: RMSEA below 0.05 = close fit, below 0.08 = acceptable;",
    "lower BIC = better.\n")



# ---- PIECE 4b: what is the third factor? ---------------------------------------
cat("\n===== STAGE 2, PIECE 4b: three-factor solution =====\n")
cat("Run time:", format(Sys.time()), "\n")

cc <- d[complete.cases(d[, items9]), items9]   # the 1,508 complete cases
n  <- nrow(cc)
R  <- cor(cc, method = "spearman")

# Three factors, promax rotation (factors allowed to correlate)
fa3 <- factanal(covmat = R, factors = 3, n.obs = n, rotation = "promax")
L3  <- unclass(fa3$loadings)

cat("\nThree-factor loadings:\n")
print(round(L3, 2))

cat("\nItems with a loading of 0.30 or more, by factor:\n")
for (j in 1:3) {
  cat("Factor", j, ":", paste(rownames(L3)[abs(L3[, j]) >= 0.30], collapse = ", "), "\n")
}

# Correlations between the three factors
Phi3 <- solve(crossprod(fa3$rotmat))
dimnames(Phi3) <- list(paste0("F", 1:3), paste0("F", 1:3))
cat("\nCorrelations between the three factors:\n")
print(round(Phi3, 2))

# Uniqueness = variance an item does NOT share; values near 0 signal a problem
cat("\nUniquenesses (values below 0.05 would be a warning sign):\n")
print(round(fa3$uniquenesses, 2))




# ---- PIECE 5: build the two scales and check their reliability -----------------
cat("\n===== STAGE 2, PIECE 5: scales and reliability =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Scale scores = mean of the items; at least half of the items must be answered
d$scale_process <- ifelse(rowSums(!is.na(d[, process_items])) >= 2,
                          rowMeans(d[, process_items], na.rm = TRUE), NA)
d$scale_malprac <- ifelse(rowSums(!is.na(d[, malprac_items])) >= 3,
                          rowMeans(d[, malprac_items], na.rm = TRUE), NA)

# 2. Description of each scale (1 = least fair ... 4 = most fair)
describe <- function(x) c(n_valid = sum(!is.na(x)), mean = round(mean(x, na.rm = TRUE), 2),
                          sd = round(sd(x, na.rm = TRUE), 2),
                          min = round(min(x, na.rm = TRUE), 2), max = round(max(x, na.rm = TRUE), 2))
cat("\nScale descriptives:\n")
print(rbind(process_fairness = describe(d$scale_process),
            malpractice      = describe(d$scale_malprac)))

# 3. Reliability: Cronbach's alpha, item-rest correlation, alpha if item dropped
reliability <- function(items, label) {
  x    <- d[complete.cases(d[, items]), items]          # respondents with all items
  k    <- ncol(x)
  v    <- cov(x)
  a_raw <- k / (k - 1) * (1 - sum(diag(v)) / sum(v))    # Cronbach's alpha
  cmat <- cor(x)
  rbar <- mean(cmat[lower.tri(cmat)])                   # average inter-item correlation
  a_std <- k * rbar / (1 + (k - 1) * rbar)              # standardized alpha
  cat("\n", label, "| respondents:", nrow(x), "| items:", k,
      "\n  alpha =", round(a_raw, 2), "| standardized alpha =", round(a_std, 2),
      "| average inter-item correlation =", round(rbar, 2), "\n")
  res <- data.frame(
    item = items,
    item_rest_r = sapply(items, function(i)
      round(cor(x[[i]], rowSums(x[, setdiff(items, i), drop = FALSE])), 2)),
    alpha_if_dropped = sapply(items, function(i) {
      xx <- x[, setdiff(items, i), drop = FALSE]
      vv <- cov(xx); kk <- ncol(xx)
      round(kk / (kk - 1) * (1 - sum(diag(vv)) / sum(vv)), 2) }))
  print(res, row.names = FALSE)
}
reliability(process_items, "PROCESS FAIRNESS scale")
reliability(malprac_items, "MALPRACTICE scale")

# 4. How strongly do the two scales relate?
cat("\nCorrelation between the two scales (Spearman):",
    round(cor(d$scale_process, d$scale_malprac, use = "complete.obs",
              method = "spearman"), 2), "\n")

# 5. Save the file for Stage 3 and close the log
write.csv(d, "data/stage2_clean.csv", row.names = FALSE)
cat("\nSaved: stage2_clean.csv\n")
sessionInfo()
sink()                                          # closes stage2_log.txt