# Writen by Terrence Gareau and Zane Witherspoon
# Analyzes feed data in R after attacks were inserted into csv by Python
# python script is feedme.py

library('rworldmap')
library('plyr')
library('ggplot2')

# Date
month <- "September 2015"

# Import Files Start -------------------
base <- read.csv("attack.csv", header = TRUE)
methodColors <- read.csv("colors.csv", header = TRUE)
methodColors$Color <- as.character(methodColors$Color)
jColors <- methodColors$Color
names(jColors) <- methodColors$Method
# Import Files End -------------------

## Footnote ---------
#https://ryouready.wordpress.com/2009/02/17/r-good-practice-adding-footnotes-to-graphics/
# basic information at the beginning of each script
scriptName <- "Attackers.R"
author <- "tuna"
footnote <- paste(scriptName, format(Sys.time(), "%d %b %Y"),
                  author, sep=" / ")

# default footnote is today's date, cex=.7 (size) and color
# is a kind of grey

makeFootnote <- function(footnoteText=
                           format(Sys.time(), "%d %b %Y"),
                         size= .7, color= grey(.5))
{
  require(grid)
  pushViewport(viewport())
  grid.text(label= footnoteText ,
            x = unit(1,"npc") - unit(2, "mm"),
            y= unit(2, "mm"),
            just=c("right", "bottom"),
            gp=gpar(cex= size, col=color))
  popViewport()
}
## Footnote

# Top10 Start -------------------
#The number 1 looked like an attack to a service provider
poo <- sort(table(base$asn),decreasing=TRUE)[1:10]
poo1 <- as.list(poo)
poo2 <- ls(poo1)

topbase <- base[which(base$asn %in% poo2),]
topbase$asn <- as.factor(topbase$asn)

#  scale_fill_brewer(palette="Paired") +
svg("attack_top10_bar.svg",width=11,height=8.5)
#  scale_fill_brewer(palette="Paired") +
print(ggplot(topbase, aes(x = asn, fill = method)) +
        ggtitle(paste("Top 10 Reflective DDoS Attacks by ASN in",month)) +
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_histogram(width = 0.7) +
        scale_fill_manual(values = jColors) +
        xlab("Observed Autonomous Systems") +
        ylab("Total Count of Attacks") +
        labs(fill = "Attack Methods"))
dev.off()
# Top10 End -------------------

# Top10 PNG Start -------------------
#The number 1 looked like an attack to a service provider
poo <- sort(table(base$asn),decreasing=TRUE)[1:10]
poo1 <- as.list(poo)
poo2 <- ls(poo1)

topbase <- base[which(base$asn %in% poo2),]
topbase$asn <- as.factor(topbase$asn)

#  scale_fill_brewer(palette="Paired") +
ppi <- 300
png("attack_top10_bar.png", width=11*ppi, height=8.5*ppi, res=ppi)
#  scale_fill_brewer(palette="Paired") +
print(ggplot(topbase, aes(x = asn, fill = method)) +
        ggtitle(paste("Top 10 Reflective DDoS Attacks by ASN in",month)) +
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_histogram(width = 0.7) +
        scale_fill_manual(values = jColors) +
        xlab("Observed Autonomous Systems") +
        ylab("Total Count of Attacks") +
        labs(fill = "Attack Methods"))
#makeFootnote(footnote)
dev.off()
# Top10 PNG End -------------------

# Top50 Start -------------------
#The number 1 looked like an attack to a service provider
poo <- sort(table(base$asn),decreasing=TRUE)[1:50]
poo1 <- as.list(poo)
poo2 <- ls(poo1)

topbase <- base[which(base$asn %in% poo2),]
topbase$asn <- as.factor(topbase$asn)

svg("attack_top50_bar.svg",width=11,height=8.5)
#  scale_fill_brewer(palette="Paired") +
print(ggplot(topbase, aes(x = asn, fill = method)) +
        ggtitle(paste("Top 50 Reflective DDoS Attacks by ASN in",month)) +
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_histogram(width = 0.7) +
        scale_fill_manual(values = jColors) +
        xlab("Observed Autonomous Systems") +
        ylab("Total Count of Attacks") +
        labs(fill = "Attack Methods") +
        coord_flip())
dev.off()
# Top50 End -------------------


# Top50 PNG Start -------------------
#The number 1 looked like an attack to a service provider
poo <- sort(table(base$asn),decreasing=TRUE)[1:50]
poo1 <- as.list(poo)
poo2 <- ls(poo1)

topbase <- base[which(base$asn %in% poo2),]
topbase$asn <- as.factor(topbase$asn)

ppi <- 300
png("attack_top50_bar.png", width=11*ppi, height=8.5*ppi, res=ppi)
#  scale_fill_brewer(palette="Paired") +
print(ggplot(topbase, aes(x = asn, fill = method)) +
        ggtitle(paste("Top 50 Reflective DDoS Attacks by ASN in",month)) +
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_histogram(width = 0.7) +
        scale_fill_manual(values = jColors) +
        xlab("Observed Autonomous Systems") +
        ylab("Total Count of Attacks") +
        labs(fill = "Attack Methods") +
        coord_flip())
dev.off()
# Top50 PNG End -------------------

# Pie Start -------------------
attacks_counts <- count(base, "method")
bp<- ggplot(attacks_counts, aes(x="", y=freq, fill=method))+
  geom_bar(width = 1, stat = "identity")
pie <- bp + coord_polar("y", start=0)

svg("attack_all_pie.svg",width=11,height=8.5)
print(pie + scale_fill_manual(values = jColors) + 
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        ggtitle(paste("Attacks by Method in",month)) +
        labs(fill = "Attack Methods") +
        ylab("Total Count of Attacks"))
dev.off()
# Pie End -------------------

# Pie PNG Start -------------------
attacks_counts <- count(base, "method")
bp<- ggplot(attacks_counts, aes(x="", y=freq, fill=method))+
  geom_bar(width = 1, stat = "identity")
pie <- bp + coord_polar("y", start=0)
ppi <- 300
png("attack_all_pie.png", width=11*ppi, height=8.5*ppi, res=ppi)
print(pie + scale_fill_manual(values = jColors) + 
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        ggtitle(paste("Attacks by Method in",month)) +
        labs(fill = "Attack Methods") +
        ylab("Total Count of Attacks"))
dev.off()
# Pie PNG End -------------------

# World Start -------------------
svg("attack_all_worldmap.svg",width=11,height=8.5)

df <- count(base$cuntry)
n <- joinCountryData2Map(df, joinCode="ISO2", nameJoinColumn="x")
mapParams <- mapCountryData(n, 
                            nameColumnToPlot="freq", 
                            mapTitle=paste("Attack Events by Country in",month),
                            addLegend=FALSE,
                            catMethod="logFixedWidth",
                            colourPalette="heat")
do.call(addMapLegend, c(mapParams
                        ,legendLabels="all"
                        ,legendWidth=1))
print(mapParams)
dev.off()

# World End -------------------

# World PNG Start -------------------
ppi <- 300
png("attack_all_worldmap.png", width=11*ppi, height=8.5*ppi, res=ppi)

df <- count(base$cuntry)
n <- joinCountryData2Map(df, joinCode="ISO2", nameJoinColumn="x")
mapParams <- mapCountryData(n, 
                            nameColumnToPlot="freq", 
                            mapTitle=paste("Attack Events by Country in",month),
                            addLegend=FALSE,
                            catMethod="logFixedWidth",
                            colourPalette="heat")
do.call(addMapLegend, c(mapParams
                        ,legendLabels="all"
                        ,legendWidth=1))
print(mapParams)
dev.off()
# World PNG End -------------------

# Attacks by day  Start -------------------
days = strtrim(base$time,10)
svg("attacks_byday_bar.svg",width=11,height=8.5)
print(ggplot(base, aes(x = days, fill = method)) +
        ggtitle(paste("Attacks by Day in",month)) +
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_histogram(width = 0.7) +
        scale_fill_manual(values = jColors) +
        xlim(rev(sort(unique((days))))) +
        xlab("Dates") +
        ylab("Total Count of Attacks") +
        labs(fill = "Attack Methods") +
        coord_flip())
dev.off()
# Attacks by day  Start -------------------

# Attacks by day PNG Start -------------------
png("attacks_byday_bar.png", width=11*ppi, height=8.5*ppi, res=ppi)
print(ggplot(base, aes(x = days, fill = method)) +
        ggtitle(paste("Attacks by Day in",month)) +
        theme(title = element_text(colour="black", face="bold")) + 
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_histogram(width = 0.7) +
        scale_fill_manual(values = jColors) +
        xlim(rev(sort(unique((days))))) +
        xlab("Dates") +
        ylab("Total Count of Attacks") +
        labs(fill = "Attack Methods") +
        coord_flip())
dev.off()
# Attacks by day PNG Start -------------------

# Attacks Durations by day PNG Start -------------------
days = strtrim(base$time,10)
png("attacks_durations_byday_scatter.png", width=11*ppi, height=8.5*ppi, res=ppi)
number_ticks <- function(n) {function(limits) pretty(limits, n)}
print(ggplot(base, aes(method, duration, color=method)) + 
        xlab("") +
        ylab("Time in Seconds") +
        ggtitle(paste("Attack Durations by Day in",month)) +
        scale_color_manual(name="Attack Methods", values = jColors) +
        theme(title = element_text(colour="black", face="bold")) +
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_jitter(shape=1, position=position_jitter(0.3)) +
        #scale_y_continuous(limits=c(0, 86400)) +
        scale_y_continuous(breaks=number_ticks(10),limits=c(0, 86400)) +
        #facet_wrap(~method, nrow=1) +
        geom_boxplot(outlier.shape = NA,col="Black",fill = NA))
dev.off()
# Attacks Durations by day PNG Start -------------------

# Attacks Durations by day SVG Start -------------------
days = strtrim(base$time,10)
svg("attacks_durations_byday_scatter.svg",width=11,height=8.5)
number_ticks <- function(n) {function(limits) pretty(limits, n)}
print(ggplot(base, aes(method, duration, color=method)) + 
        xlab("") +
        ylab("Time in Seconds") +
        ggtitle(paste("Attack Durations by Day in",month)) +
        scale_color_manual(name="Attack Methods", values = jColors) +
        theme(title = element_text(colour="black", face="bold")) +
        theme(legend.title = element_text(colour="black", size=12, face="bold")) +
        geom_jitter(shape=1, position=position_jitter(0.3)) +
        #scale_y_continuous(limits=c(0, 86400)) +
        scale_y_continuous(breaks=number_ticks(10),limits=c(0, 86400)) +
        #facet_wrap(~method, nrow=1) +
        geom_boxplot(outlier.shape = NA,col="Black",fill = NA))
dev.off()
# Attacks Durations by day SVG Start -------------------
