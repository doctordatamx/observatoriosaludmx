# Municipality drill-down, retaining the state's statistical dimensions and unknown codes.
source('R/epidemiology/build_gold.R')
build_municipal <- function() {
 manifest <- fromJSON('reports/silver_manifest.json',simplifyVector=FALSE)
 labels <- fromJSON('config/catalogue_labels.json',simplifyVector=FALSE)
 geo <- fromJSON('frontend/public/geo/index.json',simplifyVector=FALSE)
 lookup <- names(geo$names)
 hash_file<-function(path){con<-file(path,'rb');on.exit(close(con));digest::digest(readBin(con,'raw',n=file.info(path)$size),algo='sha256',serialize=FALSE)}
 algorithm_hash<-hash_file('R/spatial/build_municipal.R')
 catalogue_hash<-hash_file('config/catalogue_labels.json')
 geometry_hash<-hash_file('frontend/public/geo/index.json')
 results <- list();quality <- list()
 for(job in manifest) {
  if(job$source=='sectorial') next # No direct municipal field: never infer residency from CLUES.
  id <- paste(job$source,job$year,sep='-')
  output <- file.path('frontend/public/data/municipal',id)
  dir.create(output,recursive=TRUE,showWarnings=FALSE)
  signature<-digest::digest(paste(job$sha256,algorithm_hash,hash_file(job$silver_csv),catalogue_hash,geometry_hash,sep='|'),algo='sha256',serialize=FALSE)
  cache_file<-file.path('.runtime/municipal-cache',paste0(id,'.json'))
  if(file.exists(cache_file)) {
   cached<-fromJSON(cache_file,simplifyVector=FALSE)
   paths<-vapply(cached$info$states,function(x)paste0('frontend/public/data/',x$file),character(1))
   if(identical(cached$signature,signature)&&identical(cached$info$sha256,job$sha256)&&all(file.exists(paths))) {
    results[[id]]<-cached$info;quality[[id]]<-cached$quality;message('REUSE MUNICIPAL ',id);next
   }
  }
  message('MUNICIPAL ',id)
  d <- fread(job$silver_csv,colClasses='character',na.strings=NULL,showProgress=FALSE)
  maps <- switch(job$source,
   defunciones=c('ent_resid','mun_resid','sexo','edad','causa_def','mes_regis'),
   egresos=c('ENTIDAD','MUNIC','SEXO','EDAD','AFECPRIN','MES_ESTADISTICO'),
   urgencias=c('ENTRESIDENCIA','MUNRESIDENCIA','SEXO','EDAD','AFECPRIN','MES_ESTADISTICO'),
   lesiones=c('CodEstado','CodMunicipio','SEXO','Edad','AFECPRIN','MES_ESTADISTICO'))
  setnames(d,maps,c('state_raw','municipality_raw','sex_raw','age_raw','cause_raw','month_raw'))
  d[,state:=fifelse(grepl('^[0-9]{1,2}$',state_raw),sprintf('%02d',suppressWarnings(as.integer(state_raw))),'??')]
  d[,municipality:=fifelse(grepl('^[0-9]{1,3}$',trimws(municipality_raw)),paste0(state,sprintf('%03d',suppressWarnings(as.integer(municipality_raw)))),paste0(state,'???'))]
  d[,sex:=fifelse(sex_raw %chin% c('1','2','3'),as.integer(sex_raw),9L)]
  if(job$source=='defunciones') {
   age_codes <- labels$death_ages_by_year[[as.character(job$year)]]
   if(is.null(age_codes))stop('Missing death age dictionary')
   d[,age:=normalize_age(age_raw,rep('',.N),TRUE,names(age_codes))]
  } else d[,age:=normalize_age(age_raw,CVEEDAD)]
  d[,code:=canonical_code(cause_raw)]
  d[,cause:=fifelse(grepl('^[A-Z][0-9]{2}[A-Z0-9]?$',code),substr(code,1,3),'SIN_CODIGO')]
  d[,month:=suppressWarnings(as.integer(month_raw))]
  d[is.na(month)|month<1|month>12,month:=0L]
  info <- list();grand_total <- 0
  for(st in sort(unique(d$state))) {
   cube <- d[state==st,.(n=.N),by=.(municipality,sex,age,month,cause)]
   setorder(cube,municipality,sex,age,month,cause)
   causes <- sort(unique(cube$cause));municipalities<-sort(unique(cube$municipality))
   packed <- cbind(0L,cube$sex,cube$age,cube$month,match(cube$cause,causes)-1L,cube$n,match(cube$municipality,municipalities)-1L)
   total <- sum(cube$n);grand_total<-grand_total+total
   stopifnot(total==sum(d$state==st),!anyDuplicated(cube[,1:5]))
   data <- list(schema_version=2,columns=c('state_index','sex','age_index','month','cause_index','n','municipality_index'),states=list(st),causes=as.list(causes),municipalities=as.list(municipalities),rows=unname(packed))
   file_key<-if(grepl('^[0-9]{2}$',st))st else 'unknown'
   file <- file.path(output,paste0(file_key,'.json.gz'));temp<-paste0(file,'.part')
   con<-gzfile(temp,'w',compression=6);writeLines(toJSON(data,auto_unbox=TRUE,matrix='rowmajor'),con,useBytes=TRUE);close(con)
   stopifnot(file.copy(temp,file,overwrite=TRUE));unlink(temp)
   unmatched<-sum(cube[!municipality %chin% lookup,n])
   info[[st]]<-list(file=paste0('municipal/',id,'/',file_key,'.json.gz'),total=total,unmatched_geometry=unmatched,cells=nrow(cube),municipalities=length(municipalities))
  }
  stopifnot(grand_total==job$records,nrow(d)==job$records)
  results[[id]]<-list(source=job$source,year=job$year,states=info,total=grand_total,sha256=job$sha256)
  quality[[id]]<-list(records=job$records,aggregated_total=grand_total,unmatched_geometry=sum(vapply(info,function(x)x$unmatched_geometry,numeric(1))))
  dir.create('.runtime/municipal-cache',recursive=TRUE,showWarnings=FALSE)
  write_json(list(signature=signature,info=results[[id]],quality=quality[[id]]),cache_file,auto_unbox=TRUE,pretty=FALSE)
  rm(d,cube,packed);gc()
 }
 index<-list(schema_version=2,geometry_snapshot=geo$snapshot,geometry_vintage=geo$vintage,datasets=results,sectorial_municipal='not_available_no_direct_municipal_field',publication='local_research_only')
 write_json(index,'frontend/public/data/municipal-index.json',auto_unbox=TRUE,pretty=TRUE)
 write_json(quality,'reports/MUNICIPAL_QUALITY.json',auto_unbox=TRUE,pretty=TRUE)
 c('frontend/public/data/municipal-index.json','reports/MUNICIPAL_QUALITY.json')
}
if(sys.nframe()==0L)build_municipal()
