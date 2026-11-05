.libPaths(c('.runtime/R',.libPaths()))
library(targets)
source('R/spatial/build_municipal.R')
list(tar_target(municipal_inputs,c('reports/silver_manifest.json','config/catalogue_labels.json','frontend/public/geo/index.json',jsonlite::fromJSON('reports/silver_manifest.json')$silver_csv),format='file'),tar_target(municipal_outputs,{municipal_inputs;build_municipal();c('frontend/public/data/municipal-index.json','reports/MUNICIPAL_QUALITY.json',list.files('frontend/public/data/municipal',pattern='json.gz$',recursive=TRUE,full.names=TRUE))},format='file'))
