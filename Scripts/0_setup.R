# ============================================================
# 0_setup.R  —  Project environment setup using renv
# ============================================================

# This script:
#   1. Installs renv if not already installed
#   2. Initializes a project-local R environment
#   3. Installs required packages (edit list below)
#   4. Pins the R version
#   5. Creates/updates renv.lock for replication

message("---- Starting environment setup ----")

# ------------------------------------------------------------
# 1. Install renv if needed
# ------------------------------------------------------------
if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv")
}

library(renv)

# ------------------------------------------------------------
# 2. Initialize renv (if not already initialized)
# ------------------------------------------------------------
# renv::init() will not overwrite an existing environment.
if (!renv::project_initialized()) {
  message("Initializing renv project...")
  renv::init(bare = TRUE)
} else {
  message("renv already initialized; skipping init()")
}

# ------------------------------------------------------------
# 3. Pin the R version for reproducibility
# ------------------------------------------------------------
# Replace with the R version used for your project:
r_version <- paste(R.version$major, R.version$minor, sep = ".")
message(paste("Pinning R version:", r_version))
renv::record(paste0("rstudio/r-base@", r_version))

# ------------------------------------------------------------
# 4. Install required packages
# Created through: 
# pkgs <- renv::dependencies()$Package |> unique()
# pkgs
# ------------------------------------------------------------
packages_needed <- c(
    "renv",         
    "rmarkdown",   
    "citr",         
    "countrycode",  
    "data.table",   
    "haven",        
    "here",        
    "Hmisc",        
    "kableExtra",   
    "knitr",        
    "labelled",     
    "pals",         
    "psych",       
    "readxl",      
    "testthat",     
    "tidyverse",    
    "writexl",      
    "broom",        
    "cowplot",      
    "flextable",    
    "ggpubr",       
    "RColorBrewer",
    "pdftools",   
    )

message("Installing required packages...")

for (pkg in packages_needed) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
}

# ------------------------------------------------------------
# 5. Snapshot environment to renv.lock
# ------------------------------------------------------------
message("Creating/updating renv.lock...")
renv::snapshot(prompt = FALSE)

message("---- renv environment setup completed successfully ----")

# ------------------------------------------------------------
# 6. Instructions output
# ------------------------------------------------------------
cat(
  "\nTo reproduce this environment on another machine:\n",
  "  > install.packages('renv')\n",
  "  > renv::restore()\n\n",
  "The file renv.lock should be committed to your repository.\n",
  "Do NOT commit renv/library/.\n"
)
