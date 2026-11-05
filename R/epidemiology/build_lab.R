# Reproducible descriptive models. No population denominators or inference.
.libPaths(c('.runtime/R',.libPaths()))
library(data.table)
library(jsonlite)
setDTthreads(4L)
min_records <- 1000L
moran <- function(x,w) {
 z <- x-mean(x); s <- sum(w)
 if(length(z)<8L || s==0 || sum(z*z)<1e-20)return(NULL)
 as.numeric(length(z)/s*crossprod(z,w%*%z)/sum(z*z))
}
spatial_results <- function(x,w) {
 keep <- rowSums(w)>0
 w <- w[keep,keep,drop=FALSE]; x <- x[keep,,drop=FALSE]
 if(nrow(x)<8)return(list())
 z <- sweep(x,2,colMeans(x)); ss<-colSums(z*z)
 v <- nrow(x)/sum(w)*colSums(z*(w%*%z))/ss
 v[ss<1e-20|!is.finite(v)]<-NA_real_
 list(n=nrow(x),value=v)
}
cluster_profiles <- function(counts,top) {
 selected <- counts[,top,drop=FALSE]
 x <- sqrt(cbind(selected,other=rowSums(counts)-rowSums(selected))/rowSums(counts))
 if(nrow(x)<8||nrow(unique(x))<4)return(list())
 d <- dist(x); fit <- hclust(d,method='ward.D2'); dm<-as.matrix(d)
 groups<-lapply(2:4,function(k){
  g<-cutree(fit,k); ref<-outer(g,g,'=='); idx<-upper.tri(ref)
  sil<-vapply(seq_along(g),function(i){
   own<-which(g==g[i] & seq_along(g)!=i)
   if(!length(own))return(0)
   a<-mean(dm[i,own]); b<-min(vapply(setdiff(unique(g),g[i]),function(j)mean(dm[i,g==j]),numeric(1)))
   if(max(a,b)==0)0 else (b-a)/max(a,b)
  },numeric(1))
  stability<-mean(vapply(seq_along(top),function(j){
   alt<-cutree(hclust(dist(x[,-j,drop=FALSE]),method='ward.D2'),k)
   candidate<-outer(alt,alt,'==')
   union<-(candidate|ref)&idx
   sum(candidate&ref&idx)/sum(union)
  },numeric(1)))
  list(k=k,silhouette=mean(sil),stability=stability,groups=as.list(g))
 })
 # Euclidean classical MDS via the centered feature matrix (equivalent to PCoA).
 ord<-prcomp(x,center=TRUE,scale.=FALSE,rank.=2)
 coordinates<-ord$x[,1:2,drop=FALSE]
 retained<-sum(ord$sdev[1:2]^2)/sum(ord$sdev^2)
 distortion<-sqrt(sum((as.numeric(dist(coordinates))-as.numeric(d))^2)/sum(as.numeric(d)^2))
 mds<-list(points=lapply(seq_len(nrow(x)),function(i)list(state=rownames(x)[i],x=unname(coordinates[i,1]),y=unname(coordinates[i,2]))),retained=retained,distortion=distortion)
 list(groups=groups,mds=mds,tree=list(labels=as.list(fit$labels),order=as.list(fit$order),merge=fit$merge,height=as.list(fit$height)))
}
build_lab <- function(){
 meta<-fromJSON('frontend/public/data/index.json',simplifyVector=FALSE)$datasets
 meta<-Filter(function(d)!d$partial,meta)
 geo<-fromJSON('data/silver/lab/neighbors.json',simplifyVector=FALSE)
 keys<-sprintf('%02d',1:32)
 q<-r<-matrix(0,32,32,dimnames=list(keys,keys))
 for(edge in geo$edges){
  a<-edge[[1]];b<-edge[[2]];q[a,b]<-q[b,a]<-1
  if(isTRUE(edge[[3]]))r[a,b]<-r[b,a]<-1
 }
 months<-list()
 out<-'frontend/public/data/lab';dir.create(out,recursive=TRUE,showWarnings=FALSE)
 for(d in meta){
  f<-fread(file.path('data/silver/lab',paste0(d$id,'.csv')),colClasses=c(state='character',cause='character'))
  stopifnot(sum(f$n)==d$total)
  months[[d$id]]<-f[month %in% 1:12,.(n=sum(n)),by=.(month,cause)]
 }
 for(d in meta){
  f<-fread(file.path('data/silver/lab',paste0(d$id,'.csv')),colClasses=c(state='character',cause='character'))
  tall<-f[state %chin% keys,.(n=sum(n)),by=.(state,cause)]
  wide<-dcast(tall,state~cause,value.var='n',fill=0)
  m<-as.matrix(wide[,-1]);rownames(m)<-wide$state
  m<-m[rowSums(m)>=min_records,,drop=FALSE]
  valid<-grep('^[A-Z][0-9]{2}$',colnames(m),value=TRUE)
  top<-head(names(sort(colSums(m[,valid,drop=FALSE]),decreasing=TRUE)),12)
  clustering<-if(length(top)>=2)cluster_profiles(m,top) else list()
  x<-m[,valid,drop=FALSE]/rowSums(m)
  qm<-spatial_results(x,q[rownames(x),rownames(x),drop=FALSE])
  rm<-spatial_results(x,r[rownames(x),rownames(x),drop=FALSE])
  space<-list()
  if(length(qm)) for(code in valid)if(is.finite(qm$value[code]))space[[code]]<-list(queen=unname(qm$value[code]),rook=if(length(rm)&&is.finite(rm$value[code]))unname(rm$value[code])else NULL,n=qm$n,rook_n=if(length(rm))rm$n else NULL)
  previous<-Filter(function(v)v$source==d$source&&v$year<d$year,meta)
  anomalies<-list()
  if(length(previous)>=3L){
   all_years<-c(previous,list(d))
   observed<-rbindlist(lapply(all_years,function(v)copy(months[[v$id]])[,year:=v$year]))
   den<-observed[,.(den=sum(n)),by=.(year,month)][den>=min_records]
   grid<-den[,.(cause=valid),by=.(year,month,den)]
   grid<-observed[grid,on=.(year,month,cause)]
   grid[is.na(n),n:=0];grid[,share:=n/den]
   reference<-grid[year<d$year,.(years=.N,baseline=paste(sort(year),collapse=', '),typical=median(share),lo=min(share),hi=max(share),typical_count=median(n)),by=.(cause,month)][years>=3&typical_count>=20]
   current<-reference[grid[year==d$year],on=.(cause,month),nomatch=0]
   current[,flag:=fifelse(share>hi,'above',fifelse(share<lo,'below','inside'))]
   setorder(current,month)
   anomalies<-lapply(split(current[,.(cause,month,n,den,share,typical,lo,hi,baseline,flag)],by='cause',keep.by=FALSE),function(x)unname(lapply(split(x,seq_len(nrow(x))),as.list)))
  }
  result<-list(id=d$id,year=d$year,source=d$source,geography=d$geography,coverage=d$coverage,sha256=d$sha256,entities=nrow(m),cluster_codes=as.list(top),clusters=if(length(clustering))clustering$groups else list(),dendrogram=clustering$tree,mds=clustering$mds,moran=space,anomalies=anomalies)
  path<-file.path(out,paste0(d$id,'.json'));write_json(result,path,auto_unbox=TRUE,digits=10,null='null')
  message('LAB ',d$id)
 }
 write_json(list(vintage=geo$vintage,geometry_sha256=geo$raw_sha256,queen_edges=sum(q)/2,rook_edges=sum(r)/2,minimum_records=min_records,datasets=lapply(meta,function(d)d[c('id','source','year')])),file.path(out,'index.json'),auto_unbox=TRUE,pretty=TRUE)
}
if(sys.nframe()==0L)build_lab()


