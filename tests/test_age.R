source('R/epidemiology/build_gold.R')
stopifnot(identical(normalize_age(c('0','1','4','5','84','85','120','121','99','12'),c('5','5','5','5','5','5','5','5','9','4')),c(0L,1L,1L,2L,17L,18L,18L,19L,19L,19L)))
stopifnot(identical(normalize_age(c('1097','2001','3011','4065','4998'),rep('',5),TRUE,c('1097','2001','3011','4065','4998')),c(0L,0L,0L,14L,19L)))
cat('Age boundaries and unknown codes: PASS\n')
