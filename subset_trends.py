import sys
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

        self.trans = "gdal_translate -projwin {ulx} {uly} {lrx} {lry} {src} {dst}".format(ulx=self.xmin, uly=self.ymax,
                                                                                          lrx=self.xmax, lry=self.ymin,
                                                                                          src=self.trends_in,
                                                                                          dst=self.trends_chip)

        subprocess.call(self.trans, shell=True)

        self.data = self.read_data(self.trends_chip)

    @staticmethod
    def read_data(trends):
        """
        :param trends: <str> Full path to the Trends raster
        :return: <numpy.ndarray> Trends data read into a numpy array
        """
        src = gdal.Open(trends, gdal.GA_ReadOnly)

        if src is None:
            print(f"Error opening file: {trends}")

            sys.exit(1)

        return src.GetRasterBand(1).ReadAsArray()

    @staticmethod
    def test_data(data):
        """
        :param data: <numpy.ndarray>
        :return: <numpy.ndarray>
        """
        if np.any(data):
            mask = np.zeros_like(data, dtype=np.bool)

            mask[data > 0] = True

            return mask

        else:
            return None
