# =============================================================================
# STAGE 4: Provincial winners (H3)
# Paper:  Winning where? National and provincial differences in perceptions
#         of Pakistan's 2018 election
# Input:  stage2_clean.csv (from Stage 2)
# Output: stage4_log.txt (console log)
# Run in: RStudio, piece by piece. Edit only the SETTINGS block.
# =============================================================================

# ---- 0. SETTINGS (edit only this block) --------------------------------------
PROJECT_DIR <- "."   # the repository folder (opening winning-where.Rproj sets it)

# ---- 1. SETUP -----------------------------------------------------------------
while (sink.number() > 0) sink()                      # close any log left open earlier
setwd(PROJECT_DIR)
options(width = 200)
sink("logs/stage4_log.txt", split = TRUE, append = TRUE)

# ---- PIECE 1: the four groups and raw means ------------------------------------------
cat("\n===== STAGE 4, PIECE 1: four-way grouping and raw means =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Load the Stage 2 file and keep respondents who belong to one of the four groups
d  <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
d4 <- d[!is.na(d$group4), ]
d4$group4 <- factor(d4$group4,
                    levels = c("National winner", "National-only winner",
                               "Provincial-only winner", "Double loser"))
rownames(d4) <- NULL
cat("\nRespondents in the four groups:", nrow(d4), "of", nrow(d), "\n")

# 2. Group sizes, and who is in each group (party x province)
cat("\nGroup sizes:\n");                    print(table(d4$group4))
cat("\nGroup by province:\n");              print(table(d4$group4, d4$province))
cat("\nGroup by party:\n");                 print(table(d4$group4, d4$party))
cat("\nGroups with fewer than 30 cases:", names(which(table(d4$group4) < 30)), "\n")

# 3. Valid scale scores per group
cat("\nValid scale scores per group:\n")
print(rbind(process_fairness = tapply(!is.na(d4$scale_process), d4$group4, sum),
            malpractice      = tapply(!is.na(d4$scale_malprac),  d4$group4, sum)))

# 4. Raw means per group (higher = fairer / cleaner). Description only, not a test.
cat("\nRaw scale means by group:\n")
print(round(rbind(
  process_fairness = tapply(d4$scale_process, d4$group4, mean, na.rm = TRUE),
  malpractice      = tapply(d4$scale_malprac,  d4$group4, mean, na.rm = TRUE),
  confidence       = tapply(d4$conf_elections, d4$group4, mean, na.rm = TRUE),
  democracy_rating = tapply(d4$democracy_rating, d4$group4, mean, na.rm = TRUE),
  satisfaction     = tapply(d4$satisfaction, d4$group4, mean, na.rm = TRUE)), 2))

sink()




# ---- PIECE 2: four groups vs Double loser, with controls -----------------------------
while (sink.number() > 0) sink()
sink("logs/stage4_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 4, PIECE 2: group comparisons with controls =====\n")
cat("Run time:", format(Sys.time()), "\n")

# 1. Reload data and prepare variables (same coding as Stage 3)
d  <- read.csv("data/stage2_clean.csv", stringsAsFactors = FALSE)
d4 <- d[!is.na(d$group4), ]
d4$group4 <- factor(d4$group4, levels = c("Double loser", "National winner",
                                          "National-only winner", "Provincial-only winner"))
rownames(d4) <- NULL                                   # Double loser = reference group
d4$income3      <- factor(d4$income3, levels = c("Low", "Medium", "High"))
d4$mothertongue <- factor(d4$mothertongue,
                          levels = c("Punjabi", "Sindhi", "Pashto", "Seraiki",
                                     "Baluchi", "Hindko", "Other"))
d4$age10 <- d4$age / 10
controls <- c("age10", "female", "educ", "income3", "rural", "mothertongue",
              "interest", "days_since")

# 2. Cluster-robust SE helper (same estimator as Stage 3: CR1, df = PSUs - 1)
cluster_robust <- function(model, dat, cluster) {
  X  <- model.matrix(model); u <- residuals(model)
  cl <- cluster[match(rownames(X), rownames(dat))]
  N  <- nrow(X); k <- ncol(X); G <- length(unique(cl))
  bread <- solve(crossprod(X))
  meat  <- crossprod(rowsum(X * u, group = cl))
  V  <- bread %*% meat %*% bread * (G / (G - 1)) * ((N - 1) / (N - k))
  b  <- coef(model); se <- sqrt(diag(V)); tval <- b / se
  data.frame(estimate = b, robust_se = se,
             ci_low = b - qt(0.975, G - 1) * se, ci_high = b + qt(0.975, G - 1) * se,
             p = 2 * pt(abs(tval), df = G - 1, lower.tail = FALSE))
}

# 3. One adjusted model per outcome; print the three group contrasts vs Double loser
outcomes <- c(scale_process   = "Process fairness (1-4)",
              scale_malprac   = "Malpractice (1-4, higher = cleaner)",
              conf_elections  = "Confidence in elections (1-4)",
              democracy_rating = "How democratic the country is (1-10)",
              satisfaction    = "Satisfaction with political system (1-10)")

for (y in names(outcomes)) {
  keep <- complete.cases(d4[, c(y, "group4", controls)])
  dat  <- d4[keep, ]
  m    <- lm(reformulate(c("group4", controls), y), data = dat)
  res  <- cluster_robust(m, dat, dat$I_PSU)
  g    <- res[grep("^group4", rownames(res)), ]
  g$in_SD <- g$estimate / sd(dat[[y]])
  cat("\n---", outcomes[y], "| N =", nrow(dat), "| contrasts vs Double loser ---\n")
  print(round(g, 3))
}

sink()




# ---- PIECE 3: party comparisons within Punjab and within Sindh -----------------------
while (sink.number() > 0) sink()
sink("logs/stage4_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 4, PIECE 3: within-province party comparisons =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d4"), exists("controls"), exists("cluster_robust"))

# Run the party comparison inside one province (PTI = reference)
within_province <- function(prov, parties) {
  sub <- d4[d4$province == prov & d4$party %in% parties, ]
  sub$party <- factor(sub$party, levels = parties)               # first party = reference
  sub$mothertongue <- droplevels(sub$mothertongue)               # drop language groups absent here
  sub$income3      <- droplevels(sub$income3)
  cat("\n#################", prov, "#################\n")
  cat("Respondents by party:\n"); print(table(sub$party))
  
  for (y in names(outcomes)) {
    keep <- complete.cases(sub[, c(y, "party", controls)])
    dat  <- sub[keep, ]
    m    <- lm(reformulate(c("party", controls), y), data = dat)
    res  <- tryCatch(cluster_robust(m, dat, dat$I_PSU), error = function(e) NULL)
    if (is.null(res)) { cat("\n---", outcomes[y], ": model could not be estimated ---\n"); next }
    g <- res[grep("^party", rownames(res)), , drop = FALSE]
    g$in_SD <- g$estimate / sd(dat[[y]])
    cat("\n---", outcomes[y], "| N =", nrow(dat), "| PSUs =", length(unique(dat$I_PSU)),
        "| gap vs", parties[1], "---\n")
    print(round(g, 3))
  }
}

within_province("Punjab", c("PTI", "PML-N", "PPP"))
within_province("Sindh",  c("PTI", "PPP"))

sink()




# ---- PIECE 4: PPP supporters in Sindh vs PPP supporters elsewhere --------------------
while (sink.number() > 0) sink()
sink("logs/stage4_log.txt", split = TRUE, append = TRUE)
cat("\n===== STAGE 4, PIECE 4: PPP in Sindh vs PPP elsewhere =====\n")
cat("Run time:", format(Sys.time()), "\n")

stopifnot(exists("d4"), exists("controls"), exists("outcomes"), exists("cluster_robust"))

ppp <- d4[d4$party == "PPP", ]
ppp$in_sindh <- as.numeric(ppp$province == "Sindh")              # 1 = PPP governs the province
ppp$mothertongue <- droplevels(ppp$mothertongue)
ppp$income3      <- droplevels(ppp$income3)
cat("\nPPP supporters by province:\n"); print(table(ppp$province))
cat("\nPPP supporters, mother tongue by Sindh / elsewhere:\n")
print(table(ppp$mothertongue, ppp$in_sindh))

controls_nolang <- setdiff(controls, "mothertongue")             # main version (no language control)

out <- NULL
for (y in names(outcomes)) {
  for (spec in c("no mother tongue", "with mother tongue")) {
    ctr  <- if (spec == "no mother tongue") controls_nolang else controls
    keep <- complete.cases(ppp[, c(y, "in_sindh", ctr)])
    dat  <- ppp[keep, ]
    m    <- lm(reformulate(c("in_sindh", ctr), y), data = dat)
    res  <- tryCatch(cluster_robust(m, dat, dat$I_PSU)["in_sindh", ], error = function(e) NULL)
    if (is.null(res)) next
    out <- rbind(out, data.frame(outcome = y, spec = spec, N = nrow(dat),
                                 gap = res$estimate, se = res$robust_se,
                                 low = res$ci_low, high = res$ci_high, p = res$p,
                                 in_SD = res$estimate / sd(dat[[y]])))
  }
}
cat("\nPPP in Sindh minus PPP elsewhere (positive = more favourable in Sindh):\n")
print(format(out, digits = 2, nsmall = 2), row.names = FALSE)

sink()