# Writen by Terrence Gareau and Zane Witherspoon
# Analyzes feed data in R after scans were inserted into csv by Python
# python script is feedme.py

base <- read.csv("test.csv", header = TRUE)

#The number 1 looked like an attack to a service provider
poo <- sort(table(base$asn),decreasing=TRUE)[1:10]
poo1 <- as.list(poo)
poo2 <- ls(poo1)

topbase <- base[which(base$asn %in% poo2),]
topbase$asn <- as.factor(topbase$asn)

ggplot(topbase, aes(x = asn, fill = tmethod)) +
  ggtitle("Reflective DDoS Scans by ASN for 09-01-2015 thru 09-23-2015") +
  geom_histogram(width = 0.5) +
  xlab("Evils ASNs") +
  ylab("Total Count of Scans") +
  labs(fill = "Scan Methods")

