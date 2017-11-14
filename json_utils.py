import datetime as dt
import sys
import json
import os

import numpy as np


class JSONReader:
    def __init__(self, json_dir):
        """

        :param json_dir:
        """

        self.json_dir = json_dir

        self.json_inv = [os.path.join(self.json_dir, f) for f in os.listdir(self.json_dir)]

    @staticmethod
    def find_file(file_ls, string):
        """
        
        :param file_ls: 
        :param string: 
        :return: 
        """
        gen = filter(lambda x: string in x, file_ls)

        return next(gen, None)

    def return_json_file(self, h, v, chip_coord):
        """

        :param h:
        :param v:
        :param chip_coord:
        :return:
        """
        return self.find_file(self.json_inv, 'H{:02d}V{:02d}_{}_{}.json'.format(h, v,
                                                                                chip_coord.x_min, chip_coord.y_max))

    @staticmethod
    def find_chipcurve(results_chip, coord):
        """
        Find the results for the specified coordinate.
        :param results_chip:
        :param coord:
        :return:
        """
        with open(results_chip, 'r') as f:
            results = json.load(f)

        gen = filter(lambda x: coord.x == x['x'] and coord.y == x['y'], results)

        return next(gen, None)

    def return_json_data(self, file, pixel_coord):
        """
        
        :param file: 
        :param pixel_coord: 
        :return: 
        """

        result = self.find_chipcurve(file, pixel_coord)

        if result.get('result_ok') is True:
            return json.loads(result['result'])

    @staticmethod
    def get_json(path):
        """

        :param path:
        :return:
        """
        if os.path.exists(path):

            with open(path, 'r') as f:

                return json.load(f)

        else:

            return None

    def get_jsonchip(self, h, v, chip_coord):
        """

        :param h:
        :param v:
        :param chip_coord:
        :return:
        """
        path = self.return_json_file(h, v, chip_coord)

        try:
            return self.load_jsondata(self.get_json(path))

        except:
            # log.debug('Problem with file {}'.format(path))
            print("Unexpected error: ", sys.exc_info()[0])
            raise

    # noinspection PyTypeChecker
    @staticmethod
    def load_jsondata(data):
        """

        :param data:
        :return:
        """
        outdata = np.full(fill_value=None, shape=(100, 100), dtype=object)

        if data is not None:

            for d in data:
                result = d.get('result', 'null')

                # Could leverage geo_utils to do this
                col = int((d['x'] - d['chip_x']) / 30)
                row = int((d['chip_y'] - d['y']) / 30)

                outdata[row][col] = json.loads(result)

        return outdata

    @staticmethod
    def check_time_segment_with_training(results):
        """

        :param results:
        :return:
        """
        enforce_start = dt.datetime.toordinal(dt.datetime(1999, 12, 31))
        enforce_end = dt.datetime.toordinal(dt.datetime(2001, 1, 1))

        for num, result in enumerate(results['change_models']):

            print("\n\tChecking result {} of {}".format(num + 1, len(results['change_models'])))

            if result['start_day'] <= enforce_start and result['end_day'] >= enforce_end:

                print("Found a valid time segment")

                return 2

            elif result == results['change_models'][-1]:

                return 1

            else:

                continue

    @staticmethod
    def check_time_segment(results, start=dt.datetime(1999, 12, 31), end=dt.datetime(2001, 1, 1)):
        """

        :param results:
        :param start:
        :param end:
        :return:
        """
        enforce_start = dt.datetime.toordinal(start)
        enforce_end = dt.datetime.toordinal(end)

        for num, result in enumerate(results['change_models']):

            print("\n\tChecking result {} of {}".format(num + 1, len(results['change_models'])))

            if result['start_day'] <= enforce_start and result['end_day'] >= enforce_end:

                print("Found a valid time segment")

                return 2

            # if the last result is reached and still no valid time segment is found, return the value 1
            elif result == results['change_models'][-1]:

                return 1

            else:

                continue
