# =============================================================================
# STAGE 6: Moderation of the party gap (H5): education, political interest, sex
# Paper:  Winning where? National and provincial differences in perceptions
#         of Pakistan's 2018 election
# Input:  stage2_clean.csv (from Stage 2)
# Output: stage6_log.txt (console log)
# Run in: RStudio, piece by piece. Edit only the SETTINGS block.
# =============================================================================

# ---- 0. SETTINGS (edit only this block) --------------------------------------
PROJECT_DIR <- "."   # the repository folder (opening winning-where.Rproj sets it)

# ---- 1. SETUP -----------------------------------------------------------------
while (sink.number() > 0) sink()                      # close any log left open earlier
setwd(PROJECT_DIR)
options(width = 200)
sink("logs/stage6_log.txt", split = TRUE, append = TRUE)

# ---- PIECE 1: the moderators by party ------------------------------------------------
cat("\n===== STAGE 6, PIECE 1: moderators by party =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Load data; same comparison sample as Stage 3 (PTI, PML-N, PPP supporters)
d  <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
d6 <- d[d$party %in% c("PTI", "PML-N", "PPP"), ]
d6$party <- factor(d6$party, levels = c("PTI", "PML-N", "PPP"))     # PTI = reference
rownames(d6) <- NULL
cat("\nRespondents:", nrow(d6), "\n"); print(table(d6$party))

# 2. Education (ISCED 0-8) and political interest (1 = not at all ... 4 = very interested)
cat("\nEducation (ISCED level) distribution:\n");   print(table(d6$educ, useNA = "ifany"))
cat("\nPolitical interest distribution:\n");        print(table(d6$interest, useNA = "ifany"))

# 3. Moderators by party: means, and counts of each interest level
cat("\nMean education, mean interest, share female, by party:\n")
print(round(rbind(
  educ     = tapply(d6$educ,     d6$party, mean, na.rm = TRUE),
  interest = tapply(d6$interest, d6$party, mean, na.rm = TRUE),
  female   = tapply(d6$female,   d6$party, mean, na.rm = TRUE)), 2))

cat("\nParty by political interest (counts):\n");   print(table(d6$party, d6$interest))
cat("\nParty by education level (counts):\n");      print(table(d6$party, d6$educ))

# 4. How strongly are education and interest related (they could overlap)?
cat("\nSpearman correlation, education and interest:",
    round(cor(d6$educ, d6$interest, method = "spearman", use = "complete.obs"), 2), "\n")

sink()




# ---- PIECE 2: party x education and party x political interest -----------------------
while (sink.number() > 0) sink()
sink("logs/stage6_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 6, PIECE 2: party x education, party x political interest =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Reload data and prepare variables (same coding as Stages 3-4)
d  <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
d6 <- d[d$party %in% c("PTI", "PML-N", "PPP"), ]
d6$party <- factor(d6$party, levels = c("PTI", "PML-N", "PPP"))
rownames(d6) <- NULL
d6$income3      <- factor(d6$income3, levels = c("Low", "Medium", "High"))
d6$mothertongue <- factor(d6$mothertongue,
                          levels = c("Punjabi", "Sindhi", "Pashto", "Seraiki",
                                     "Baluchi", "Hindko", "Other"))
d6$age10 <- d6$age / 10
controls_all <- c("age10", "female", "educ", "income3", "rural", "mothertongue",
                  "interest", "days_since")
outcomes <- c(scale_process    = "Process fairness",
              scale_malprac    = "Malpractice (higher = cleaner)",
              conf_elections   = "Confidence in elections",
              democracy_rating = "How democratic the country is",
              satisfaction     = "Satisfaction with political system")

# 2. Cluster-robust covariance (CR1, PSU clusters): returns coefficients, covariance, PSU count
cr_vcov <- function(model, dat, cluster) {
  X  <- model.matrix(model); u <- residuals(model)
  cl <- cluster[match(rownames(X), rownames(dat))]
  N  <- nrow(X); k <- ncol(X); G <- length(unique(cl))
  bread <- solve(crossprod(X))
  meat  <- crossprod(rowsum(X * u, group = cl))
  V <- bread %*% meat %*% bread * (G / (G - 1)) * ((N - 1) / (N - k))
  list(b = coef(model), V = V, G = G)
}

# 3. Interaction models for one moderator
run_mod <- function(modvar, drop_ctrl, label, standardize = TRUE) {
  ctr  <- setdiff(controls_all, drop_ctrl)             # moderator enters via the interaction
  rows <- NULL
  for (y in names(outcomes)) {
    keep <- complete.cases(d6[, c(y, "party", modvar, ctr)])
    dat  <- d6[keep, ]
    dat$mod <- if (standardize) as.numeric(scale(dat[[modvar]])) else dat[[modvar]]
    m  <- lm(reformulate(c("party * mod", ctr), y), data = dat)
    cv <- cr_vcov(m, dat, dat$I_PSU)
    nm <- c("partyPML-N:mod", "partyPPP:mod")
    b  <- cv$b[nm]; se <- sqrt(diag(cv$V))[nm]
    p  <- 2 * pt(abs(b / se), cv$G - 1, lower.tail = FALSE)
    W  <- as.numeric(t(b) %*% solve(cv$V[nm, nm]) %*% b)          # joint Wald test of both terms
    pj <- pf(W / 2, 2, cv$G - 1, lower.tail = FALSE)
    rows <- rbind(rows, data.frame(
      outcome = outcomes[y], N = nrow(dat),
      PMLN_x_mod = b[1], PMLN_se = se[1], PMLN_p = p[1],
      PPP_x_mod  = b[2], PPP_se  = se[2], PPP_p  = p[2], joint_p = pj,
      PMLN_in_SD = b[1] / sd(dat[[y]])))
  }
  rownames(rows) <- NULL
  cat("\n---", label, "---\n")
  print(format(rows, digits = 2, nsmall = 3), row.names = FALSE)
}

cat("\nInteraction = change in the gap vs PTI per 1 SD of the moderator (positive = gap shrinks).\n")
run_mod("educ",     drop_ctrl = "educ",     label = "Party x EDUCATION (per 1 SD)")
run_mod("interest", drop_ctrl = "interest", label = "Party x POLITICAL INTEREST (per 1 SD)")

sink()




# ---- PIECE 3: sex moderation + subgroup gaps (PML-N vs PTI) --------------------------
while (sink.number() > 0) sink()
sink("logs/stage6_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 6, PIECE 3: sex moderation and subgroup gaps =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d6"), exists("controls_all"), exists("outcomes"),
          exists("cr_vcov"), exists("run_mod"))

# 1. Party x sex (female = 1), interaction per unit (female vs male)
cat("\nInteraction = how much larger/smaller the gap vs PTI is for women than for men.\n")
run_mod("female", drop_ctrl = "female", label = "Party x SEX (women vs men)", standardize = FALSE)

# 2. Subgroups: adjusted PML-N vs PTI gap within each education and interest group
d6$educ_grp <- cut(d6$educ, breaks = c(-1, 1, 3, 8),
                   labels = c("None/primary", "Secondary", "Post-secondary+"))
d6$int_grp  <- cut(d6$interest, breaks = c(0, 2, 4), labels = c("Low interest", "High interest"))
pp <- d6[d6$party %in% c("PTI", "PML-N"), ]
pp$pml <- as.numeric(pp$party == "PML-N")

subgap <- function(grpvar, drop_ctrl) {
  out <- NULL
  for (g in levels(pp[[grpvar]])) {
    s <- pp[which(pp[[grpvar]] == g), ]
    s$mothertongue <- droplevels(s$mothertongue); s$income3 <- droplevels(s$income3)
    ctr <- setdiff(controls_all, drop_ctrl)
    for (y in names(outcomes)) {
      keep <- complete.cases(s[, c(y, "pml", ctr)]); dat <- s[keep, ]
      m  <- lm(reformulate(c("pml", ctr), y), data = dat)
      cv <- tryCatch(cr_vcov(m, dat, dat$I_PSU), error = function(e) NULL)
      if (is.null(cv)) next
      b <- cv$b["pml"]; se <- sqrt(cv$V["pml", "pml"])
      out <- rbind(out, data.frame(group = g, outcome = outcomes[y],
                                   n_PTI = sum(dat$pml == 0), n_PMLN = sum(dat$pml == 1),
                                   gap = b, se = se,
                                   p = 2 * pt(abs(b / se), cv$G - 1, lower.tail = FALSE)))
    }
  }
  rownames(out) <- NULL
  print(format(out, digits = 2, nsmall = 3), row.names = FALSE)
}
cat("\n--- PML-N minus PTI gap within EDUCATION groups (adjusted) ---\n"); subgap("educ_grp", "educ")
cat("\n--- PML-N minus PTI gap within INTEREST groups (adjusted) ---\n");  subgap("int_grp", "interest")

sink()