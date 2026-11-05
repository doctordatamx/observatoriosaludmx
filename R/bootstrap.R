dir.create('.runtime/R', recursive=TRUE, showWarnings=FALSE)
.libPaths(c('.runtime/R',.libPaths()))
if (!requireNamespace('renv',quietly=TRUE)) install.packages('renv',lib='.runtime/R',repos='https://cloud.r-project.org')
renv::restore(lockfile='renv.lock',library='.runtime/R',prompt=FALSE)
