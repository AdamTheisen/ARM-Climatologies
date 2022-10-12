# ARM-Climatologies
## Prelude
This repository will serve as a living paper to document climatologies at the Atmospheric Radiation User Facility sites and is open to anyone that would like to expand on the existing work.  If used for your research, please cite the DOI.

[![DOI](https://zenodo.org/badge/505950468.svg)](https://zenodo.org/badge/latestdoi/505950468)

## Background
The [Atmospheric Radiation Measurement User Facility](https://arm.gov/) (ARM) is a multi-laboratory U.S. Department of Energy (DOE) scientific user facility and key contributor to national and international climate research efforts.  ARM operates three fixed and three mobile facilities that operate all over the world (Turner and Ellingson 2016).  The Southern Great Plain (SGP) observatory in Oklahoma is the most-extensive climate research facility in the world and has data dating back to 1993 (Sisterson et al 2016).  The North Slope of Alaska (NSA) observatory in Utquiavik, AK came online in 2003 (Verlinde et al 2016).  Eastern North Atlantic Observatory (ENA) site located in Graciosa Island, Azores came online in 2013.  Three ARM Mobile Facilities (AMF) travel around the world on 6-24 month deployments for the first two AMFs and roughly 5-year deployments for the third mobile facility (Miller et al. 2016).  ARM has been the source for a number of climatology-related studies focues on aerosol radiative properties (Andrews et al. 2011), surface cloud radiative effects (McFarlane, Long, Flaherty 2013), aerosol optical depth (Michalsky et al. 2010), and others (Kollias et al. 2007, Dong et al. 2006) but to the author's knowledge, very little work has been done on basic climatology of surface meteorology at the ARM fixed sites.  This repository will serve as the location to document ongoing climatology efforts.

## Data Quality
ARM applies basic quality control tests such as minimum, maximum, and delta tests to flag outliers (Table 1) (Peppler et al. 2016).  The results of these tests are stored in the data files in bit-packed quality control (QC) variables.  ARM employs instrument experts, called instrument mentors, that oversee each instruments operations and ensure the quality of the data. These mentors work closely with the ARM Data Quality (DQ) Office to monitor the data for any QC problems.  When found, these problems are communicated to site operations and others as appropriate to work towards resolving the issues.  Once the problem has been resolved, a Data Quality Report (DQR) is submitted that is visible in the [Data Discovery timeline](https://adc.arm.gov/discovery/#/results/id::nsametC1.b1_atmos_pressure_sfcmet_met_sfcmet?dataLevel=b1&showDetails=true) and accessible through a [webservice](https://code.arm.gov/docs/dqrws-examples/-/wikis/home).  These DQRs provide a quality category (Missing, Suspect, Incorrect, Note), date ranges, description, and more and can be applied to additionally threshold the data.  The program (arm_climatology.py) in this repository uses the [Atmospheric data Community Toolkit (ACT)](https://github.com/ARM-DOE/ACT) (Theisen et al. 2022) to download and add DQRs to the existing quality control variables and tests.  In order to calculate the averages, all data flagged by QC variables and DQRs are excluded from the mean.  Additionally, the number of samples used in each average is also written out to the file.  No further QC is performed at this moment and it is assumed that the ARM data record is well-documented.  Data from this program are written out into csv files in the results folder and plots are created with the plot_climatology.py program are available in the images directory.

Table 1. Minimum, maximum, and delta thresholds for each fixed site based on the latest file headers as of June 21, 2022.
| Site | Minimum | Maximum | Delta |
| ---- | ------- | ------- | ----- |
| SGP  | -40 ºC  | 50 ºC   | 20 ºC |
| NSA  | -60 ºC  | 30 ºC   | 10 ºC |
| ENA  |   5 ºC  | 30 ºC   | 20 ºC |

## Results
### North Slope of Alaska
#### Temperature
The NSA monthly temperatures from both the ARM and NOAA (NOOA Climate Reference Network) sites (Fig. 1) show a notable period from 2014-2019 where the average temperatures over the winter were higher as compared to the data from 2005-2013.   In both datasets, there was a significant decrease in the monthly averages during the 2019-2020 winter.  As shown in Figure 1, the agreement between the ARM and NOAA monthly averages validates that the ARM and NOAA temperature records are consistent and the slight deviations that are present are due to missing periods of data (black circle and sqaures). Yearly averaged temperature are likewise, very similar as shown in Figure 2.  As noted, the increase in temperatures from 2014-2019 is visible in the yearly averages with that significant decrease in 2020 In Figures 1 and 2, the larger black dot indicate months where there were less than 25 days worth of data used to produce that average and as such likely has some bias.  Data for these periods can be found in the [results](https://github.com/AdamTheisen/ARM-Climatologies/tree/main/results) area of this repository.


![ARM and NOAA Monthly Average Temperatures](https://github.com/AdamTheisen/ARM-Climatologies/blob/main/images/nsametC1.b1_temp_mean_nsa60noaacrnX1.b1_temperature_M.png)
Figure 1. Monthly average temperatures from ARM (blue) and NOAA (orange).

![ARM and NOAA Yearly Average Temperatures](https://github.com/AdamTheisen/ARM-Climatologies/blob/main/images/nsametC1.b1_temp_mean_nsa60noaacrnX1.b1_temperature_Y.png)
Figure 2. Yearlly average temperatures from ARM (blue) and NOAA (orange).

In visualizing these data another way (Fig. 3), the spread in the temperatures over the winter months, espcially in January to March is clear compared with summer months.  The monthly values can be found in Table 2 and indicate that July 2019 was the warmest on record since 2004 by 1.4ºC and the 2017-2019 period including 3 of the 5 warmest July's on record.

![ARM Monthly Average Temperatures](https://github.com/AdamTheisen/ARM-Climatologies/blob/main/images/nsametC1.b1_temp_mean_by_month.png)
Figure 3. Monthly average temperatures plotted by month and color-coded by year.

Table 2. ARM monthly average temperatures. 
![ARM Monthly Average Temperature Table](https://github.com/AdamTheisen/ARM-Climatologies/blob/main/images/nsametC1.b1_temp_mean_table.png)

#### Precipitation
There has been a lack of reliable precipitation measurements at the ARM NSA site.  A total precipitation sensor (TPS; Hotplate) was deployed from 2006-2014 but the quality of the measurements is unknown.  The ARM MET system also had a present weather detector deployed but generally thos have not been reliable in frozen precipitation.  More recently (Spring 2017), two Thies laser precipitation monitor, two FlowCapt solid particle mass flux sensors and an array of sonic snow depth sensors have been deployed at the NSA site with more instrumentation soon to be deployed at a new extended facility, NSA E12.  The NOAA facility did have a weighing bucket rain gauge deployed (Fig. 4) as part of the U.S. Climate Reference Network which shows a general increease in precipitation from 2017-2019, coinciding with the warmer average temperatures.  There is likely also some erroneous data in 2004 which should be ignored.  Monthly totals (Fig. 5) generally show minimal precipitation during the winter months as expected with a non-heated tipping bucket rain gauge but outside of a few cases, no single month has recieved more than 50 mm of precipitation.  More efforts to verify these totals with more recent ARM measurements and to investigate snow fall climatologies at the NSA site.

![ARM Yearly Precipitation Totals](https://github.com/AdamTheisen/ARM-Climatologies/blob/main/images/nsa60noaacrnX1.b1_precipitation_Y.png)
Figure 4. Yearly total precipitation from the NOAA weighing bucket rain gauge.

![ARM Monthly Precipitation Totals](https://github.com/AdamTheisen/ARM-Climatologies/blob/main/images/nsa60noaacrnX1.b1_precipitation_M.png)
Figure 5. Monthly total precipitation from the NOAA weighing bucket rain gauge.

## Conclusions
This repository will serve as a single point of reference for ongoing climatology results for the ARM fixed sites.  The analysis will be expanded to the other fixed sites and updated on a yearly basis.  Additional statistics, instruments, and variables will be added as requested and time permits. In the results for NSA, it is clear to see that there has been some significant changes in the averages over time at the NSA site, most notable with prolonged periods of warmer winters which did lead to increases in observed liquid precipitation.  Additional efforts are needed to verify the precipitation measurements as there are some quality concerns.  It is vital that ARM and NOAA continue to collect high-quality data in this region to track future changes.

## References
Andrews, E., Ogren, J. A., Bonasoni, P., Marinoni, A., Cuevas, E., Rodríguez, S., ... & Sheridan, P. (2011). Climatology of aerosol radiative properties in the free troposphere. Atmospheric Research, 102(4), 365-393.

Dong, X., Xi, B., & Minnis, P. (2006). A climatology of midlatitude continental clouds from the ARM SGP central facility. Part II: Cloud fraction and surface radiative forcing. Journal of climate, 19(9), 1765-1783.

Kollias, P., Tselioudis, G., & Albrecht, B. A. (2007). Cloud climatology at the Southern Great Plains and the layer structure, drizzle, and atmospheric modes of continental stratus. Journal of Geophysical Research: Atmospheres, 112(D9).

Kyrouac, J., & Shi, Y. Surface Meteorological Instrumentation (MET). Atmospheric Radiation Measurement (ARM) User Facility. https://doi.org/10.5439/1786358

McFarlane, S. A., Long, C. N., & Flaherty, J. (2013). A Climatology of Surface Cloud Radiative Effects at the ARM Tropical Western Pacific Sites, Journal of Applied Meteorology and Climatology, 52(4), 996-1013. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/apme/52/4/jamc-d-12-0189.1.xml

Michalsky, J., Denn, F., Flynn, C., Hodges, G., Kiedron, P., Koontz, A., ... & Schwartz, S. E. (2010). Climatology of aerosol optical depth in north‐central Oklahoma: 1992–2008. Journal of Geophysical Research: Atmospheres, 115(D7).

Miller, M. A., Nitschke, K., Ackerman, T. P., Ferrell, W. R., Hickmon, N., & Ivey, M. (2016). The ARM Mobile Facilities, Meteorological Monographs, 57, 9.1-9.15. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-15-0051.1.xml

NOAA Climate Reference Network (60NOAACRN). Atmospheric Radiation Measurement (ARM) User Facility.

Peppler, R. A., Kehoe, K. E., Monroe, J. W., Theisen, A. K., & Moore, S. T. (2016). The ARM Data Quality Program, Meteorological Monographs, 57, 12.1-12.14. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-15-0039.1.xml

Sisterson, D. L., Peppler, R. A., Cress, T. S., Lamb, P. J., & Turner, D. D. (2016). The ARM Southern Great Plains (SGP) Site, Meteorological Monographs, 57, 6.1-6.14. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-16-0004.1.xml

Adam Theisen, Ken Kehoe, Zach Sherman, Bobby Jackson, Alyssa Sockol, Corey Godine, Max Grover, Jason Hemedinger, Jenni Kyrouac, Maxwell Levin, & Michael Giansiracusa. (2022). ARM-DOE/ACT: v1.1.5 (v1.1.5). Zenodo. https://doi.org/10.5281/zenodo.6502861

Turner, D. D., & Ellingson, R. G. (2016). Introduction, Meteorological Monographs, 57, v-x. Retrieved Jun 21, 2022, from https://journals.ametsoc.org/view/journals/amsm/57/1/amsmonographs-d-16-0001.1.xml
