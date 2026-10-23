# Winning where? National and provincial differences in perceptions of Pakistan's 2018 election

Replication materials for the article:

"Winning Where? National and Provincial Differences in Perceptions of Pakistan's 2018 Election." *Journal name*, forthcoming.

The repository contains the code, the numerical results and the figures behind every table and figure in the article and its online appendix. The survey data are not included because distribution of the world values survey data is restricted.

## Overview

The study uses the Pakistan survey of the seventh wave of the World Values Survey (WVS-7; N = 1,995; fieldwork 4 November to 11 December 2018). It asks whether supporters of the nationally governing party (PTI) and of the two main opposition parties (PML-N and PPP) judge the 2018 general election differently, whether winning in one's own province matters alongside winning nationally, and whether party supporters read the survey items on vote counting and election officials in the same way.

| Hypothesis | Stage | Script | Article |
|---|---|---|---|
| Data preparation and coding | 1 | `R/stage1_data_preparation.R` | Section 3, Table 1 |
| Two integrity dimensions (factor analysis, scales) | 2 | `R/stage2_factor_analysis.R` | Section 3 |
| H1, H2: party gaps; process fairness vs malpractice | 3 | `R/stage3_party_comparison.R` | Table 2, Figure 1 |
| H3: national and provincial winners | 4 | `R/stage4_provincial_winners.R` | Table 3 |
| H4: item-level differences (ordinal logistic DIF) | 5 | `R/stage5_item_dif.R` | Table 4, Figure 2 |
| H5: moderation by education and political interest | 6 | `R/stage6_moderation.R` | Figure 3 |
| Independent re-estimation in Python | 7 | `python/stage7_python_verification.py` | Section 3 (software), Online Appendix |
| Tables and figures from the logs | 8 | `tables_figures/*.py` | All tables and figures |

## Repository structure

```
.
├── R/                  Stages 1-6 (R)
├── python/             Stage 7, independent verification (Python)
├── tables_figures/     Stage 8: reads the logs and builds the tables and figures
├── figures/            Figures 1-3 and Figure A1 (300 dpi PNG)
├── data/               Place the WVS file here (not distributed; see data/README.md)
├── requirements.txt    Python packages
├── CITATION.cff
└── LICENSE
```

## Data

The analysis uses the WVS-7 Pakistan data. The World Values Survey Association distributes the data free of charge for non-commercial research, but its terms do not allow redistribution, so the data file is not part of this repository. To reproduce the analysis, download the Pakistan data from the [World Values Survey website](https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp) and follow the instructions in [`data/README.md`](data/README.md).

Data citation: Haerpfer, Christian, Ronald Inglehart, Alejandro Moreno, Christian Welzel, Kseniya Kizilova, Jaime Diez-Medrano, Marta Lagos, Pippa Norris, Eduard Ponarin, and Bi Puranen, eds. 2022. *World Values Survey: Round Seven – Country-Pooled Datafile*. Madrid and Vienna: JD Systems Institute and WVSA Secretariat.

## Software

The results in the article were produced with the versions below on Windows 11.

- **R 4.6.1**: `readxl` 1.5.0.1, `dplyr` 1.2.1, `sandwich`, `lmtest`, `MASS` (MASS ships with R). Stage 1 installs `readxl` and `dplyr` if they are missing; install `sandwich` and `lmtest` beforehand with `install.packages(c("sandwich", "lmtest"))` (Stage 3 checks that they are present).
- **Python 3.14.2**: numpy 2.4.4, pandas 3.0.2, scipy 1.18.0, statsmodels 0.15.0, openpyxl 3.1.5 (Stage 7); matplotlib and python-docx (Stage 8). Install with `python -m pip install -r requirements.txt`.

## How to reproduce

1. Place the data file in `data/` as described in `data/README.md`.
2. Run the R scripts in order, Stage 1 to Stage 6. Each script runs top to bottom and writes its console output to `logs/`. Stages 1 and 2 write the analysis files `data/stage1_clean.csv` and `data/stage2_clean.csv`.
3. Run the verification from the repository folder: `python python/stage7_python_verification.py`.
4. Build the results, figures and tables:
   ```
   python tables_figures/parse_logs.py
   python tables_figures/figures.py
   python tables_figures/build_main.py
   python tables_figures/build_appendix.py
   ```
   The tables are written to `paper/Main_Tables_Figures.docx` and `paper/Online_Appendix.docx`.

## Analytical notes

- Estimates are unweighted. The Pakistan file carries a constant weight.
- Standard errors are clustered by primary sampling unit (CR1 correction), with t-tests on G − 1 degrees of freedom.
- Random seeds are fixed at 2018 (parallel analysis in Stage 2, cluster bootstraps in Stages 3 and 5).
- Stage 7 re-codes the raw data and re-estimates the Stage 3 and Stage 4 models in Python. The results match the R estimates (see `logs/stage7_log.txt`).

## License

The code is released under the MIT License (see `LICENSE`). The logs, results and figures are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The WVS data remain subject to the World Values Survey Association's terms of use.

## Citation

If you use these materials, please cite the article above. Citation metadata are in `CITATION.cff`.

## Contact

Saima Naseem, reach@saimanaseem.com
