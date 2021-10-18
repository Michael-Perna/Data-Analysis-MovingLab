# MovingLab

# Description 
NTRIP client for Swisspos,

0. **rmv-files-by-format.py** : Used to clean the DataBase repository from ghosts files of previous computations (GUI not available)

1. **relative-precision.py** : This script read the .snmea data output by the parse-nmea_plus.py from the ParserNmea reporsitory and it applied the MNN95 projection and calulate the orthogonal distance from the rail distance. The output has the format .results and is given only for positions which are recognized as part of the TPG railway 12, therefore multiple files are created which each corresponds to one tram trajecory on on an associated referenced. (GUI available and work both on single files than recursibvly on any level of folder)

2. **concatTracks.py**: This script merge all .results data from the database of a specific reveciver and applied the rails/loop.shp which mask all the unwanted position. This script can also be used to select GNSS position inside particualra geographic area defined in the shapefile inside ./maps/areas-of-intrest.  (GUI available to select folder to merge and give type of receiver, the selcetion of the area is not available trhoug GUI yet). The output is given in ./res/data/

3. **statistic.py** : this script compute an ensemble of statistical analysis and plot on each separate receiver (it read the data inside ./res/data/ with the format .data). No GUI available. It also create as output a .csv file usefull to work with the positions in qgis for example. 

# NTRIP_Client




# Table-of-Content
# Installation
# Usage
# Contributing
# Credits & References
# License

# News:
# Next step
