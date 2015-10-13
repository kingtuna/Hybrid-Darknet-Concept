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
