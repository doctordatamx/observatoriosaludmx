# R owns epidemiological definitions and aggregation. No models/rates here.
.libPaths(c('.runtime/R', .libPaths()))
library(data.table)
library(jsonlite)
setDTthreads(4)
age_groups <- c('<1','1-4',paste(seq(5,80,5),seq(9,84,5),sep='-'),'85+','Sin dato v\u00e1lido')
normalize_age <- function(value, unit, death=FALSE, known_death_codes=NULL) {
  v <- suppressWarnings(as.integer(value)); u <- suppressWarnings(as.integer(unit))
  years <- rep(NA_real_,length(v))
  if (death) {
    known <- value %in% known_death_codes
    years[known & v >= 1000 & v < 4000] <- 0
    ok <- known & v >= 4000 & v <= 4120
    years[ok] <- v[ok]-4000
  } else {
    ok <- !is.na(v) & !is.na(u) & u==5 & v>=0 & v<=120
    years[ok] <- v[ok]
    baby <- !is.na(v) & !is.na(u) & ((u==2 & v>=0 & v<=23) | (u==3 & v>=0 & v<=30) | (u==4 & v>=0 & v<=11))
    years[baby] <- 0
  }
  g <- rep(19L,length(v))
  g[!is.na(years) & years<1] <- 0L
  g[!is.na(years) & years>=1 & years<5] <- 1L
  ok <- !is.na(years) & years>=5 & years<85
  g[ok] <- as.integer(floor(years[ok]/5))+1L
  g[!is.na(years) & years>=85] <- 18L
  g
}
canonical_code <- function(x) toupper(gsub('.', '', trimws(x),fixed=TRUE))
build_gold <- function() {
 manifest <- fromJSON('reports/silver_manifest.json', simplifyVector=FALSE)
 labels <- fromJSON('config/catalogue_labels.json',simplifyVector=FALSE)
 dir.create('frontend/public/data',recursive=TRUE,showWarnings=FALSE)
 dir.create('data/gold',recursive=TRUE,showWarnings=FALSE)
 manifest <- manifest[order(vapply(manifest,function(x)x$source,character(1)),vapply(manifest,function(x)x$year,numeric(1)))]
 meta <- list(); quality <- list()
 for (job in manifest) {
  id <- paste(job$source,job$year,sep='-')
  message('GOLD ',id)
  d <- fread(job$silver_csv,colClasses='character',na.strings=NULL,showProgress=FALSE)
  stopifnot(nrow(d)==job$records)
  maps <- switch(job$source,
    defunciones=c('ent_resid','sexo','edad','causa_def','mes_regis'),
    egresos=c('ENTIDAD','SEXO','EDAD','AFECPRIN','MES_ESTADISTICO'),
    urgencias=c('ENTRESIDENCIA','SEXO','EDAD','AFECPRIN','MES_ESTADISTICO'),
    lesiones=c('CodEstado','SEXO','Edad','AFECPRIN','MES_ESTADISTICO'),
    sectorial=c('CEDOCVE','SEXO','EDAD1','AFECPRIN4','MES'))
  setnames(d,maps,c('state_raw','sex_raw','age_raw','cause_raw','month_raw'))
  d[,state:=fifelse(grepl('^[0-9]{1,2}$',state_raw),sprintf('%02d',suppressWarnings(as.integer(state_raw))),'??')]
  d[,sex:=fifelse(sex_raw %chin% c('1','2','3'),as.integer(sex_raw),9L)]
  if (job$source=='defunciones') {
    age_codes <- labels$death_ages_by_year[[as.character(job$year)]]
    if (is.null(age_codes)) stop(paste('Missing year-specific death age catalogue',job$year))
    d[,age:=normalize_age(age_raw,rep('',.N),TRUE,names(age_codes))]
  } else {
    unit_col <- if(job$source=='sectorial') 'CLAVE_EDAD' else 'CVEEDAD'
    d[,age:=normalize_age(age_raw,get(unit_col))]
  }
  d[,code:=canonical_code(cause_raw)]
  d[,cause:=fifelse(grepl('^[A-Z][0-9]{2}[A-Z0-9]?$' ,code),substr(code,1,3),'SIN_CODIGO')]
  d[,month:=suppressWarnings(as.integer(month_raw))]
  d[is.na(month) | month<1 | month>12,month:=0L]
  cube <- d[,.(n=.N),by=.(state,sex,age,month,cause)]
  setorder(cube,state,sex,age,month,cause)
  stopifnot(sum(cube$n)==nrow(d), all(cube$n>0), !anyDuplicated(cube[,1:5]))
  causes <- sort(unique(cube$cause)); states <- sort(unique(cube$state))
  # Compact tuples use indices into explicit dictionaries; no microdata leave Silver.
  packed <- cbind(match(cube$state,states)-1L,cube$sex,cube$age,cube$month,match(cube$cause,causes)-1L,cube$n)
  counts <- list(records=nrow(d),cube_total=sum(cube$n),cube_cells=nrow(cube),unknown_age=sum(d$age==19),unknown_sex=sum(d$sex==9),invalid_cause_format=sum(d$cause=='SIN_CODIGO'),unknown_month=sum(d$month==0),nonstandard_state=sum(!d$state %chin% sprintf('%02d',1:32)))
  coverage <- switch(job$source,defunciones='Defunciones registradas \u00b7 INEGI/SS',egresos='Egresos institucionales reportados a DGIS',urgencias='Atenciones de urgencias reportadas a DGIS',lesiones='Registros de lesiones reportados a DGIS',sectorial='Egresos del sector salud \u00b7 serie separada')
  geography <- switch(job$source,lesiones='Entidad de ocurrencia del evento',sectorial='Entidad de atenci\u00f3n','Entidad de residencia habitual')
  calendar <- if(job$source=='defunciones') 'Mes de registro' else 'Mes estad\u00edstico'
  data <- list(schema_version=1,columns=c('state_index','sex','age_index','month','cause_index','n'),states=states,causes=causes,rows=unname(packed))
  path <- paste0('frontend/public/data/',id,'.json.gz')
  con <- gzfile(path,'w',compression=6);writeLines(toJSON(data,auto_unbox=TRUE,matrix='rowmajor'),con,useBytes=TRUE);close(con)
  info <- list(id=id,source=job$source,year=job$year,total=nrow(d),coverage=coverage,geography=geography,calendar=calendar,cutoffs=job$cutoffs,partial=job$year==2026,months=sort(unique(d$month[d$month>0])),url=job$url,sha256=job$sha256,file=paste0(id,'.json.gz'),bytes=file.info(path)$size,quality=counts,status='Exploraci\u00f3n local \u00b7 conciliaci\u00f3n externa pendiente')
  meta[[length(meta)+1L]] <- info;quality[[id]]<-counts
  rm(d,cube,packed);gc()
 }
 index <- list(updated='2026-11-04',local_only=TRUE,age_groups=age_groups,states=labels$states,causes=labels$causes,datasets=meta,methodology='METODOLOGIA.md')
 write_json(index,'frontend/public/data/index.json',auto_unbox=TRUE,pretty=TRUE,null='null')
 write_json(quality,'reports/GOLD_QUALITY.json',auto_unbox=TRUE,pretty=TRUE)
 write_json(meta,'data/gold/manifest.json',auto_unbox=TRUE,pretty=TRUE)
 'frontend/public/data/index.json'
}
if (sys.nframe()==0L) build_gold()
