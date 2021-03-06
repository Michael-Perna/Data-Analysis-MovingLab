# MovingLab
Data-Analysis-MovingLab analyses and compare the GNSS data generates by three differents GNSS receivers in a dynamicaly mode and urban environment. MovingLab which is the name of the benchmarch system was composed of a Trimble Zephyr Rover 3 antenna which distributed his signal to the follow receivers: 
- Trimble NetR9 with RTK from swipos services
- u-blox ZED-F9P with RTK from swipos services
- u-blox ZED-F9P with PPP-RTK from sapcorda services (today PointPerfect of u-blox)

The MovingLab was mounted on a tram of the line 9 in Geneva and collected data for many months.


# Description
## Important Folders
- **Data** contains the observations of the theodolite campaign, the xsens IMU and the GNSS receivers data test on the swisstopo roof. 
- **DataBase** contains all the observations taken by the GNSS receiveres onboard of the MovingLab. Which included the raw NMEA (in .txt format) and the parsed and processed data (.SNMEA & .results format). The observations are structure in a database which separate the data for each day). 
- **res** contains the analysed GNSS data for each receiver and zone of intrest (in .csv format, easly to import in QGIS).

## Function 
### **rmv-files-by-format.py**
Used to clean the DataBase repository from ghosts files of previous computations (GUI not available)
### **unzip_batch.py**
Used to unzip the RINEX files of the Trimble NetR9 receiver

## GNSS Receivers analysis

Data Analysis of all NMEA measurements used during the MovingLAb project

### 1. **relative-precision.py**
This script read the .snmea data output by the parse-nmea_plus.py from the ParserNmea reporsitory and it applied the MNN95 projection and calulate the orthogonal distance from the rail distance. The output has the format .results and is given only for positions which are recognized as part of the TPG railway 12, therefore multiple files are created which each corresponds to one tram trajecory on on an associated referenced. (GUI available and work both on single files than recursibvly on any level of folder)

### 2. **concatTracks.py** (Integrated inside statistic)
This script merge all .results data from the database of a specific reveciver and applied the rails/loop.shp which mask all the unwanted position. This script can also be used to select GNSS position inside particualra geographic area defined in the shapefile inside ./maps/areas-of-intrest.  (GUI available to select folder to merge and give type of receiver, the selcetion of the area is not available trhoug GUI yet). The output is given in ./res/data/

### 3. **statistic.py**
this script compute an ensemble of statistical analysis and plot on each separate receiver (it read the data inside ./res/data/ with the format .data). No GUI available. It also create as output a .csv file usefull to work with the positions in qgis for example. 

## Referenceses: theodolites & IMU 
### **theodolites.py**
analyses the meausures taken by theodolites
### **xsens.py**
Analyse the xsens measurements

# 

# Contributing & Credits
- Le??la Kislig : supervisor at swisstopo
- Jan Skaloud : academic supervisor at EPFL
- Daniel Willi : lib/geolib/swissprojection (under license)

I thank the Transport Public Genevois (TPG) for their help and support

# Further step
## 1. Analysis
- Compare GNSS receivers epochs-by-epochs

- Improve theodolites anaysis

- End xsens IMU amalysis

## 2. Optimize Code
- concatTracks should be removed and integrate inside relative-precision as this is an inefficient way to proced. Which duplicate the data in a new format and it increase the saving space.  DONE :) 
- 


