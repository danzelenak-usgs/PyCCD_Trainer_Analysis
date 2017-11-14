import os
import sys
import numpy as np
from osgeo import gdal
import glob
import subprocess

from geo_utils import ChipExtents
from subset_trends import SubsetTrends
from json_utils import JSONReader

WKT = '''PROJCS["Albers",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378140,298.2569999999957,AUTHORITY["EPSG",
"7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]],
PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],
PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["false_easting",0],
PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'''


class CheckTrainingData:
    def __init__(self, h=5, v=2, in_trends=r"Z:\ancillary\training\trends.tif",
                 out_dir=r"C:\Users\dzelenak\Workspace\LCMAP_Eval\ARD_h05v02\class\ancillary",
                 json_dir=r'Z:\sites\washington\pyccd-results\H05V02\2017.06.20\json'):

        self.in_trends = in_trends
        self.out_dir = out_dir
        self.out_trends = self.out_dir + os.sep + "trends_chips"

        if not os.path.exists(self.out_trends):
            os.makedirs(self.out_trends)

        self.H = h
        self.V = v

        self.JSON_DIR = json_dir

        self.chip_info = ChipExtents(self.H, self.V)

        self.chip_extents = self.chip_info.CHIP_EXTENTS

        # self.json_tools = JSONReader(self.JSON_DIR)

    def analyze_chips(self):

        counter = 1.0

        json_reader = JSONReader(self.JSON_DIR)

        for chip in self.chip_extents:

            current = counter / len(self.chip_extents) * 100.0

            print("\nAnalyzing Chip {} of 2500\n".format(chip))

            # subset the CONUS trends to the current chip extent
            trends_chip = self.out_trends + os.sep + "trends_{}.tif".format(chip)

            if os.path.exists(trends_chip):
                os.remove(trends_chip)

            trends = SubsetTrends(self.in_trends, trends_chip, self.chip_extents[chip])

            # Store a reference to the trends data for the current chip in a flattened array
            trends_data = trends.data.flatten()

            # Generate a mask for the current chip based on that chips' Trends subset
            # trends_mask is true where trends_data > 0
            trends_mask = trends.test_data(trends_data)

            # If trends_mask is True anywhere, that means there is Trends data present for the current chip
            if np.any(trends_mask):
                print("\n\tFound Trends data for chip {}\n".format(chip))

                # Create a new array similar to trends_mask, but will contain values 0, 1, 2
                out_mask = np.zeros_like(trends_data, dtype=np.uint8).flatten()

                # Anywhere in the chip with Trends data gets value 1 in the out_mask array
                out_mask[trends_data > 0] = 1

                # Pull the json results for the current chip, store as a flattened array, keep values in the array
                # where the trends_mask is True
                json_results = json_reader.get_jsonchip(h=self.H,
                                                        v=self.V,
                                                        chip_coord=self.chip_extents[chip]).flatten()[trends_mask]

                sliced = out_mask[trends_mask]

                for index, result in enumerate(json_results):

                    if len(result['change_models']) > 0:
                        # TODO implement logging

                        sliced[index] = json_reader.check_time_segment_with_training(results=result)

                    else:
                        # Case for when PyCCD coverage = 0, still count as good Trends Data
                        sliced[index] = 1

                out_mask[trends_mask] = sliced

                out_mask = out_mask.reshape((100, 100))

                print("\nGenerating new raster from time_segment & trends mask\n")

                if np.any(out_mask):
                    self.array_to_raster(chip=chip, mask=out_mask, rsc=trends_chip)

            # show the percent complete
            sys.stdout.write("\r%s%% Done " % str(current)[:5])

            # needed to display the current percent complete
            sys.stdout.flush()

            counter += 1.0

        sys.stdout.flush()

        return None

    def array_to_raster(self, chip, mask, rsc):
        """

        :param chip:
        :param mask:
        :param rsc:
        :return:
        """
        driver = gdal.GetDriverByName("GTiff")

        out_str = self.out_dir + "{a}chips{a}mask_{b}.tif".format(a=os.sep, b=chip)

        if not os.path.exists(os.path.split(out_str)[0]):
            os.makedirs(os.path.split(out_str)[0])

        outfile = driver.Create(out_str, 100, 100, 1, gdal.GDT_Byte)

        outband = outfile.GetRasterBand(1)
        outband.WriteArray(mask, 0, 0)

        geo = (self.chip_extents[chip].x_min, 30.0, 0.0, self.chip_extents[chip].y_max, 0.0, -30.0)

        outfile.SetGeoTransform(geo)
        outfile.SetProjection(WKT)

        outfile, outband = None, None

        return None

    @staticmethod
    def assemble_chips(indir):
        """

        :param indir: Path to the directory containing the chip masks
        :return:
        """
        infiles = glob.glob(indir + os.sep + "*.tif")

        outfile = indir + os.sep + "mosaic.tif"

        merge = f"gdal_merge.py -o {outfile} -v {' '.join(infiles)}"

        subprocess.call(merge, shell=True)

        return None

    def graph_results(self):

        # TODO produce graphs showing quantities w/o valid time segments for each Trends class

        pass


class CheckTimeSegments:
    def __init__(self, h, v, json_dir, out_dir):
        """

        :param h:
        :param v:
        :param json_dir:
        :param out_dir:
        """

        self.H = h
        self.V = v

        self.json_dir = json_dir

        self.out_dir = out_dir
        self.out_dir = self.out_dir + os.sep + "time_seg_masks"

        self.chip_info = ChipExtents(self.H, self.V)

        self.chip_extents = self.chip_info.CHIP_EXTENTS

        # self.json_tools = JSONReader(self.json_dir)

    def analyze_time_segments(self):
        """

        :return:
        """
        # TODO write each chip array to a larger array that will contain the results for the entire tile
        json_reader = JSONReader(self.json_dir)

        counter = 1.0

        for chip in self.chip_extents:

            current = counter / 2500.0 * 100.0

            mask = np.zeros(shape=(100, 100), dtype=np.uint8).flatten()

            json_results = json_reader.get_jsonchip(h=self.H, v=self.V, chip_coord=self.chip_extents[chip]).flatten()

            for index, result in enumerate(json_results):

                if len(result["change_models"]) > 0:

                    mask[index] = json_reader.check_time_segment(results=result)

                else:

                    # case for NoData within a tile
                    mask[index] = 0

            out_mask = mask.reshape((100, 100))

            if np.any(out_mask):
                self.array_to_raster(chip=chip, mask=out_mask)

            sys.stdout.write("\r%s%% Done " % str(current)[:5])

            # needed to display the current percent complete
            sys.stdout.flush()

            counter += 1.0

        sys.stdout.flush()

        return None

    def array_to_raster(self, chip, mask):
        """

        :param chip:
        :param mask:
        :return:
        """
        driver = gdal.GetDriverByName("GTiff")

        out_str = self.out_dir + "{a}chips{a}mask_{b}.tif".format(a=os.sep, b=chip)

        if not os.path.exists(os.path.split(out_str)[0]):
            os.makedirs(os.path.split(out_str)[0])

        outfile = driver.Create(out_str, 100, 100, 1, gdal.GDT_Byte)

        outband = outfile.GetRasterBand(1)

        outband.WriteArray(mask, 0, 0)

        geo = (self.chip_extents[chip].x_min, 30.0, 0.0, self.chip_extents[chip].y_max, 0.0, -30.0)

        outfile.SetGeoTransform(geo)
        outfile.SetProjection(WKT)

        outband, outfile = None, None

        return None
