# Track 1 & Track 2 — R environment (one library, both tracks)
# Rscript environment/install.R
#
# Registers the R kernel with Jupyter (IRkernel::installspec()) so the
# notebooks/*/r.ipynb files show up with a working "R" kernel, and are
# runnable in RStudio regardless.

pkgs <- c(
  "tidyverse", "ggplot2", "patchwork", "plotly",
  "sf", "leaflet",
  "shiny",
  "forecast", "tidymodels",
  "fairness",
  "DBI", "RSQLite", "httr2",         # Track 1: connectivity (Module 2)
  "pointblank",                       # Track 1: validation (Module 8)
  "plumber",                          # Track 1: optional API extension (Module 2)
  "IRkernel"
)

installed <- rownames(installed.packages())
to_install <- setdiff(pkgs, installed)
if (length(to_install) > 0) {
  install.packages(to_install, repos = "https://cloud.r-project.org")
}

# Optional, heavier install — Module 7's Prophet alternative:
# install.packages("prophet")

IRkernel::installspec(name = "ir", displayname = "R")

cat("\nDone. Open any notebooks/*/r.ipynb in Jupyter, or open apps/shiny_app.R directly in RStudio.\n")
