read_pilot <- function(path) {
  x <- jsonlite::fromJSON(path)
  stopifnot(nrow(x$data) == 14L, all(x$data$count >= 0), !anyDuplicated(x$data[c("year", "series")]))
  x
}
