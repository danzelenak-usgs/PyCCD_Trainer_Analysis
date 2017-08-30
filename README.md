# PyCCD_Trainer_Analysis

# Requirements:
Python >= 3.6

gdal == 2.2.1

# Purpose:
To determine the overlap between Trends Land Cover and valid time segments.  A time segment is currently considered valid if it begins before 12/31/1999 and ends after 1/1/2001 (using the start_day and end_day values).

# Parameters required by CheckTrainingData:

h = Horizontal ARD Grid Identifier

v = Vertical ARD Grid Identifier

in_trends = Path to the CONUS Trends Land Cover year 2000 tif file

out_dir = Path to where subfolders and output files will be saved (currently chip-subset Trends, and Trends+Time_Segment Chip Masks)

json_dir = Path to the location of json files containing PyCCD results for the current tile

The method "analyze_chips" can then be called without any passed arguments to automatically generate results

Currently hardcoded to run on tile H05V02, but other tiles can be specified in the call to "CheckTrainingData"

# Example:

from analyze_pyccd_training_data import CheckTrainingData

h5v2 = CheckTrainingData()

h5v2.analyze_chips()

h4v1 = CheckTrainingData(h=4, v=1, in_trends=r"Z:\trendspath", out_dir=r"Z:\outpath", json_dir=r"Z:\jsonpath")

h4v1.analyze_chips()

