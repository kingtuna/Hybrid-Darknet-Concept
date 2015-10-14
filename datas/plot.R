# Import Files Start -------------------
setwd("~/Documents/workspace/R/feed")
base <- read.csv("attack.csv", header = TRUE)
methodColors <- read.csv("colors.csv", header = TRUE)
methodColors$Color <- as.character(methodColors$Color)
jColors <- methodColors$Color
names(jColors) <- methodColors$Method
# Import Files End -------------------

date <- as.Date(base$date)
base10time <- as.integer(base$base10time)
str(base$base10time)
plot(date,
     base10time,
     type = "p",
     pch = 21,
     #lwd = 16,
     col=c(jColors)[base$method],
     main = "Time of Day Attacked",
     xlab="Date",
     ylab="Hour")

library(scatterplot3d)
scatterplot3d(base$date,
              base$method,
              base10time, 
              color = c(jColors)[base$method],
              pch = 21,
              type="p",
              main="3D Scatterplot")

plot(base$duration,base$method, main="Scatterplot Example", 
     xlab="Car Weight ", ylab="Miles Per Gallon ")

library(ggplot2)
library(scales)
library(gridExtra)

month <- "September 2015"
number_ticks <- function(n) {function(limits) pretty(limits, n)}
print(ggplot(base, aes(method, duration, color=method)) + 
        xlab("") +
        ylab("Time in Seconds") +
        ggtitle(paste("Attacks Durations by Day in",month)) +
        scale_color_manual(name  ="Attack Methods", values = jColors) +
        theme(title = element_text(colour="black", face="bold")) +
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_jitter(shape=1, position=position_jitter(0.3),alpha = 1) +
        #scale_y_continuous(limits=c(0, 86400)) +
        scale_y_continuous(breaks=number_ticks(10),limits=c(0, 86400)) +
        arrangeGrob(p, sub = textGrob("Footnote", x = 0, hjust = -0.1, vjust=0.1, gp = gpar(fontface = "italic", fontsize = 18))) +
        #facet_wrap(~method, nrow=1) +
        text("DICKS", 1) +
      geom_boxplot(outlier.shape = NA,col="Black",fill = NA))

