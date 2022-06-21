# ARM-Climatologies

## Background
The [Atmospheric Radiation Measurement User Facility](https://arm.gov/) (ARM) is a multi-laboratory U.S. Department of Energy (DOE) 
scientific user facility and key contributor to national and international climate research efforts.  ARM operates three fixed and 
three mobile facilities that operate all over the world (Turner and Ellingson 2016).  The Southern Great Plain (SGP) observatory in 
Oklahoma is the most-extensive climate research facility in the world and has data dating back to 1993 (Sisterson et al 2016).  
The North Slope of Alaska (NSA) observatory in Utquiavik, AK came online in 2003 (Verlinde et al 2016).  
Eastern North Atlantic Observatory (ENA) site located in Graciosa Island, Azores came online in 2013.  
Three ARM Mobile Facilities (AMF) travel around the world on 6-24 month deployments for the first two AMFs and roughly 5-year deployments 
for the third mobile facility (Miller et al. 2016).  ARM has been the source for a number of climatology-related studies focues on aerosol 
radiative properties (Andrews et al. 2011), surface cloud radiative effects (McFarlane, Long, Flaherty 2013), aerosol optical depth 
(Michalsky et al. 2010), and others (Kollias et al. 2007, Dong et al. 2006) but to the author's knowledge, very little work has been 
done on basic climatology of surface meteorology at the ARM fixed sites.  This repository will serve as the location to document ongoing 
climatology efforts.

## Data Quality
ARM applies basic quality control tests such as minimum, maximum, and delta tests to flag outliers (Table 1) (Peppler et al. 2016).  
The results of these tests are stored in the data files in bit-packed quality control (QC) variables.  ARM employs instrument experts 
, called instrument mentors, that oversee each instruments operations and ensure the quality of the data. These mentors work closely 
with the ARM Data Quality (DQ) Office to monitor the data for any QC problems.  When found, these problems are communicated to site 
operations and others as appropriate to work towards resolving the issues.  Once the problem has been resolved, a Data Quality Report 
(DQR) is submitted that is visible in the [Data Discovery timeline](https://adc.arm.gov/discovery/#/results/id::nsametC1.b1_atmos_pressure_sfcmet_met_sfcmet?dataLevel=b1&showDetails=true) and accessible through a [webservice](https://code.arm.gov/docs/dqrws-examples/-/wikis/home).  
These DQRs provide a quality category (Missing, Suspect, Incorrect, Note), date ranges, description, and more and can be applied to 
additionally threshold the data.  The program (arm_climatology.py) in this repository uses the 
[Atmospheric data Community Toolkit (ACT)](https://github.com/ARM-DOE/ACT) (Theisen et al. 2022) to download and add DQRs to the existing 
quality control variables and tests.  In order to calculate the averages, all data flagged by QC variables and DQRs are excluded from the mean.  
Additionally, the number of samples used in each average is also written out to the file.  No further QC is performed at this moment and it is assumed that the ARM data record is well-documented.  Data from this program are written out into csv files in the results folder and plots are 
created with the plot_climatology.py program are available in the images directory.

Table 1. Minimum, maximum, and delta thresholds for each fixed site based on the latest file headers as of June 21, 2022.
| Site | Minimum | Maximum | Delta |
| ---- | ------- | ------- | ----- |
| SGP  | -40 ºC  | 50 ºC   | 20 ºC |
| NSA  | -60 ºC  | 30 ºC   | 10 ºC |
| ENA  |   5 ºC  | 30 ºC   | 20 ºC |

## Results
### North Slope of Alaska



## References
Andrews, E., Ogren, J. A., Bonasoni, P., Marinoni, A., Cuevas, E., Rodríguez, S., ... & Sheridan, P. (2011). Climatology of aerosol radiative properties in the free troposphere. Atmospheric Research, 102(4), 365-393.

Dong, X., Xi, B., & Minnis, P. (2006). A climatology of midlatitude continental clouds from the ARM SGP central facility. Part II: Cloud fraction and surface radiative forcing. Journal of climate, 19(9), 1765-1783.

Kollias, P., Tselioudis, G., & Albrecht, B. A. (2007). Cloud climatology at the Southern Great Plains and the layer structure, drizzle, and atmospheric modes of continental stratus. Journal of Geophysical Research: Atmospheres, 112(D9).

McFarlane, S. A., Long, C. N., & Flaherty, J. (2013). A Climatology of Surface Cloud Radiative Effects at the ARM Tropical Western Pacific Sites, Journal of Applied Meteorology and Climatology, 52(4), 996-1013. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/apme/52/4/jamc-d-12-0189.1.xml

Michalsky, J., Denn, F., Flynn, C., Hodges, G., Kiedron, P., Koontz, A., ... & Schwartz, S. E. (2010). Climatology of aerosol optical depth in north‐central Oklahoma: 1992–2008. Journal of Geophysical Research: Atmospheres, 115(D7).

Miller, M. A., Nitschke, K., Ackerman, T. P., Ferrell, W. R., Hickmon, N., & Ivey, M. (2016). The ARM Mobile Facilities, Meteorological Monographs, 57, 9.1-9.15. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-15-0051.1.xml

Peppler, R. A., Kehoe, K. E., Monroe, J. W., Theisen, A. K., & Moore, S. T. (2016). The ARM Data Quality Program, Meteorological Monographs, 57, 12.1-12.14. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-15-0039.1.xml

Sisterson, D. L., Peppler, R. A., Cress, T. S., Lamb, P. J., & Turner, D. D. (2016). The ARM Southern Great Plains (SGP) Site, Meteorological Monographs, 57, 6.1-6.14. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-16-0004.1.xml

Adam Theisen, Ken Kehoe, Zach Sherman, Bobby Jackson, Alyssa Sockol, Corey Godine, Max Grover, Jason Hemedinger, Jenni Kyrouac, Maxwell Levin, & Michael Giansiracusa. (2022). ARM-DOE/ACT: v1.1.5 (v1.1.5). Zenodo. https://doi.org/10.5281/zenodo.6502861

Turner, D. D., & Ellingson, R. G. (2016). Introduction, Meteorological Monographs, 57, v-x. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-16-0001.1.xml
