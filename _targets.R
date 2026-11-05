.libPaths(c('.runtime/R', .libPaths()))
library(targets)
source('R/epidemiology/build_gold.R')
tar_option_set(packages = c('jsonlite', 'data.table'))
list(
 tar_target(silver_manifest, 'reports/silver_manifest.json', format='file'),
 tar_target(silver_inputs, {
  m <- jsonlite::fromJSON(silver_manifest)
  c(m$silver_csv, 'config/catalogue_labels.json')
 }, format='file'),
 tar_target(web_index, {
  silver_inputs
  build_gold()
 }, format='file')
)
