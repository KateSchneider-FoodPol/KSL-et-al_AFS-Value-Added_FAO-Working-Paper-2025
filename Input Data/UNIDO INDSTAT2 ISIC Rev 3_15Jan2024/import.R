inst.classes <- c("factor","factor","factor","factor","factor","numeric","factor","factor","factor")
inst.names  <- c("ctable","country","year","isic","isiccomb","value","utable","source","unit")
inst        <- read.csv(file="data.csv", header=FALSE, col.names=inst.names, colClasses=inst.classes, na.strings="...")