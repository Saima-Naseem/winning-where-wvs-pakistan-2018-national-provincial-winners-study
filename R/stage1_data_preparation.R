# =============================================================================
# STAGE 1: Data preparation
# Paper:   Winning where? National and provincial differences in perceptions
#          of Pakistan's 2018 election
# Data:    WVS-7 Pakistan 2018 (N = 1,995), sheet "original" (raw codes)
# Output:  stage1_clean.csv (analysis file), stage1_log.txt (console log)
# Run in:  RStudio, top to bottom. Nothing outside the SETTINGS block needs editing.
# =============================================================================

# ---- 0. SETTINGS (edit only this block) --------------------------------------
PROJECT_DIR <- "."   # the repository folder (opening winning-where.Rproj sets it)
DATA_FILE   <- "data/WVS_Pak_Data.xlsx"
ELECTION_DATE <- as.Date("2018-07-25")     # used to compute days since the election

# ---- 1. SETUP -----------------------------------------------------------------
pkgs <- c("readxl", "dplyr")
to_install <- setdiff(pkgs, rownames(installed.packages()))
if (length(to_install) > 0) install.packages(to_install)   # installs only if missing
library(readxl); library(dplyr)

setwd(PROJECT_DIR)
options(width = 200)                       # wider console so tables do not wrap
sink("logs/stage1_log.txt", split = TRUE)       # print to console AND save to a log file

# ---- 2. LOAD RAW DATA -----------------------------------------------------------
raw <- read_excel(DATA_FILE, sheet = "original")
names(raw) <- sub(":.*$", "", names(raw))  # headers look like "Q224: How often..." -> "Q224"
stopifnot(nrow(raw) == 1995)               # stop early if the wrong file/sheet is read

# Variables this paper needs; the script stops if any is absent
needed <- c("Q224","Q225","Q226","Q227","Q228","Q229","Q230","Q231","Q232", # nine integrity items
            "Q76",  "Q251", "Q252",                                         # regime evaluation
            "Q223", "N_REGION_WVS", "J_INTDATE",                            # party, province, date
            "Q262", "Q275", "Q288", "Q260", "H_URBRURAL", "Q290", "Q199",   # controls
            "I_PSU")                                                        # cluster ID (for Stage 3 onward)
missing_vars <- setdiff(needed, names(raw))
if (length(missing_vars) > 0) stop("Not found in file: ", paste(missing_vars, collapse = ", "))
raw <- raw %>% mutate(across(all_of(needed), as.numeric))

# ---- 3. OUTCOMES: missing codes -> NA, then align direction ----------------------
# WVS missing codes are negative (-1 don't know, -2 no answer, -3/-5 not applicable).
clean_missing <- function(x) ifelse(x < 0, NA, x)

# Fairness items: raw 1 = "very often" = HIGH integrity, so reverse (5 - x)
fair_items <- c(pf_counted = "Q224", pf_journalists = "Q228",
                pf_officials = "Q229", pf_choice = "Q232")
# Malpractice items: raw 1 = "very often" = LOW integrity, so keep as is
# (higher = malpractice occurs less often = cleaner election)
malp_items <- c(mp_blocked = "Q225", mp_tvbias = "Q226", mp_bribery = "Q227",
                mp_richbuy = "Q230", mp_violence = "Q231")

d <- data.frame(I_PSU = raw$I_PSU)
for (nm in names(fair_items)) d[[nm]] <- 5 - clean_missing(raw[[fair_items[nm]]])
for (nm in names(malp_items)) d[[nm]] <- clean_missing(raw[[malp_items[nm]]])

d$conf_elections   <- 5 - clean_missing(raw$Q76)   # reversed: higher = more confidence
d$democracy_rating <- clean_missing(raw$Q251)      # 1-10, higher = more democratic
d$satisfaction     <- clean_missing(raw$Q252)      # 1-10, higher = more satisfied

# Keep "don't know" flags (raw -1) so we can study who answers "don't know"
all_items <- c(fair_items, malp_items)
for (nm in names(all_items)) d[[paste0("dk_", nm)]] <- as.numeric(raw[[all_items[nm]]] == -1)

# ---- 4. PARTY PREFERENCE ------------------------------------------------------------
# Q223 asks about a hypothetical vote "tomorrow", not the 2018 vote.
d$party <- case_when(
  is.na(raw$Q223) | raw$Q223 < 0 ~ NA_character_,   # blank or DK/NA stays missing
  raw$Q223 == 586007             ~ "PTI",
  raw$Q223 == 586002             ~ "PML-N",
  raw$Q223 == 586001             ~ "PPP",
  raw$Q223 == 2                  ~ "Would not vote",
  TRUE                           ~ "Other")          # incl. 586003 (PML, other faction)

# ---- 5. PROVINCE AND FOUR-WAY WINNER/LOSER GROUPING -----------------------------------
d$province <- case_when(
  raw$N_REGION_WVS == 586010 ~ "Punjab",
  raw$N_REGION_WVS == 586011 ~ "Sindh",
  raw$N_REGION_WVS == 586012 ~ "KP",
  raw$N_REGION_WVS == 586013 ~ "Balochistan")

# PTI governed the centre, Punjab and KP; PPP held Sindh (as stated in the paper)
d$group4 <- case_when(
  d$party == "PTI" & d$province %in% c("Punjab", "KP")         ~ "National winner",
  d$party == "PTI" & d$province %in% c("Sindh", "Balochistan") ~ "National-only winner",
  d$party == "PPP" & d$province == "Sindh"                     ~ "Provincial-only winner",
  d$party == "PML-N"                                           ~ "Double loser",
  d$party == "PPP" & d$province != "Sindh"                     ~ "Double loser")

# ---- 6. CONTROLS -------------------------------------------------------------------------
d$female   <- as.numeric(raw$Q260 == 2)
d$age      <- clean_missing(raw$Q262)
d$educ     <- clean_missing(raw$Q275)                       # ISCED 0-8
d$income3  <- case_when(raw$Q288 %in% 1:3 ~ "Low",          # collapsed as in the cleaning log
                        raw$Q288 %in% 4:7 ~ "Medium",
                        raw$Q288 %in% 8:10 ~ "High")
d$rural    <- as.numeric(raw$H_URBRURAL == 2)
d$mothertongue <- case_when(
  raw$Q290 == 586001 ~ "Punjabi",  raw$Q290 == 586004 ~ "Sindhi",
  raw$Q290 == 586006 ~ "Pashto",   raw$Q290 == 586008 ~ "Seraiki",
  raw$Q290 == 586003 ~ "Baluchi",  raw$Q290 %in% c(586007, 586009) ~ "Hindko",  # two Hindko codes merged
  raw$Q290 %in% c(586005, 586999) ~ "Other")
d$interest   <- 5 - clean_missing(raw$Q199)                 # reversed: higher = more interested
d$int_date   <- as.Date(as.character(raw$J_INTDATE), format = "%Y%m%d")
d$days_since <- as.numeric(d$int_date - ELECTION_DATE)      # days from election to interview

# ---- 7. SAFETY CHECKS (script stops if a recode went wrong) ---------------------------------
stopifnot(all(d$pf_counted %in% c(1:4, NA)),
          all(d$mp_violence %in% c(1:4, NA)),
          all(d$conf_elections %in% c(1:4, NA)),
          all(d$democracy_rating %in% c(1:10, NA)))
cat("Rows:", nrow(d), "| Days since election, min-max:",
    paste(range(d$days_since, na.rm = TRUE), collapse = " to "), "\n")

# ---- 8. DATA-QUALITY SUMMARY (send me this part) ----------------------------------------------
outcomes <- c(names(fair_items), names(malp_items),
              "conf_elections", "democracy_rating", "satisfaction")

cat("\n=== Party preference ===\n");            print(table(d$party, useNA = "ifany"))
cat("\n=== Province ===\n");                    print(table(d$province, useNA = "ifany"))
cat("\n=== Party by province ===\n");           print(table(d$party, d$province, useNA = "ifany"))
cat("\n=== Four-way grouping ===\n");           print(table(d$group4, useNA = "ifany"))
cat("\n=== Four-way grouping by province ===\n"); print(table(d$group4, d$province))
cat("\nGroups with fewer than 30 cases:\n");    print(names(which(table(d$group4) < 30)))

cat("\n=== Share missing (DK or NA) by party ===\n")
print(d %>% filter(!is.na(party)) %>% group_by(party) %>%
        summarise(n = n(), across(all_of(outcomes), ~ round(mean(is.na(.x)), 3))), width = Inf)

cat("\n=== Share answering 'don't know' by party ===\n")
print(d %>% filter(!is.na(party)) %>% group_by(party) %>%
        summarise(across(starts_with("dk_"), ~ round(mean(.x, na.rm = TRUE), 3))), width = Inf)

cat("\n=== Direction check: outcome means by party (not a result, only a sanity check) ===\n")
print(d %>% filter(party %in% c("PTI", "PML-N", "PPP")) %>% group_by(party) %>%
        summarise(across(all_of(outcomes), ~ round(mean(.x, na.rm = TRUE), 2))), width = Inf)

# ---- 9. SAVE ----------------------------------------------------------------------------------------
write.csv(d, "data/stage1_clean.csv", row.names = FALSE)
cat("\nSaved: stage1_clean.csv\n")
sessionInfo()                              # records R and package versions for the methods note
sink()