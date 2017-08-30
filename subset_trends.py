import os
from osgeo import gdal
import subprocess
import numpy as np


class SubsetTrends:

    def __init__(self, trends_in, trends_chip, extent, cellsize=30):

        self.trends_in = trends_in
        self.trends_chip = trends_chip

        self.cellsize = cellsize

        self.xmin = extent.x_min
        self.xmax = extent.x_max
        self.ymin = extent.y_min
        self.ymax = extent.y_max

        self.src = gdal.Open(self.trends_in, gdal.GA_ReadOnly)

        self.trans = "gdal_translate -projwin {ulx} {uly} {lrx} {lry} {src} {dst}".format(ulx=self.xmin, uly=self.ymax,
                                                                                     lrx=self.xmax, lry=self.ymin,
                                                                                     src=self.trends_in,
                                                                                     dst=self.trends_chip)

        subprocess.call(self.trans, shell=True)

        self.data = self.read_data(self.trends_chip)

    def read_data(self, trends):
        """
        :param trends: 
        :return: 
        """

        src = gdal.Open(trends, gdal.GA_ReadOnly)

        return src.GetRasterBand(1).ReadAsArray()

    def test_data(self, data):
        """
        :param data: 
        :return: 
        """

        if np.any(data):

            mask = np.zeros_like(data, dtype=np.bool)

            mask[ data > 0 ] = True

            return mask

        else:

            return None





