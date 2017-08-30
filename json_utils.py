import os
import json
import datetime as dt
import numpy as np


class JSONReader:

    def __init__(self, json_dir):

        self.json_dir = json_dir

        self.json_inv = [os.path.join(self.json_dir, f) for f in os.listdir(self.json_dir)]

    def find_file(self, file_ls, string):
        """
        
        :param file_ls: 
        :param string: 
        :return: 
        """

        gen = filter(lambda x: string in x, file_ls)

        return next(gen, None)

    def return_json_file(self, h, v, chip_coord):
        """
        
        :param chip_coord: 
        :return: 
        """

        return self.find_file(self.json_inv, 'H{:02d}V{:02d}_{}_{}.json'.format(h, v,
                                                                         chip_coord.x_min, chip_coord.y_max))

    def find_chipcurve(self, results_chip, coord):
        """
        Find the results for the specified coordinate.
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

    def get_json(self, path):

        if os.path.exists(path):

            with open(path, 'r') as f:

                return json.load(f)

        else:

            return None

    def get_jsonchip(self, h, v, chip_coord):

        path = self.return_json_file(h, v, chip_coord)

        try:

            return self.load_jsondata(self.get_json(path))

        except:
            # log.debug('Problem with file {}'.format(path))
            raise

    # noinspection PyTypeChecker
    def load_jsondata(self, data):

        outdata = np.full(fill_value=None, shape=(100, 100), dtype=object)

        if data is not None:

            for d in data:

                result = d.get('result', 'null')

                # Could leverage geo_utils to do this
                col = int((d['x'] - d['chip_x']) / 30)
                row = int((d['chip_y'] - d['y']) / 30)

                outdata[row][col] = json.loads(result)

        return outdata

    def check_time_segment(self, results):

        # start_dates = []
        # end_dates = []

        enforce_start = dt.datetime.toordinal(dt.datetime(1999, 12, 31))
        enforce_end = dt.datetime.toordinal(dt.datetime(2001, 1, 1))

        for num, result in enumerate(results['change_models']):

            print("\n\tChecking result {} of {}".format(num+1, len(results['change_models'])))

            if result['start_day'] <= enforce_start and result['end_day'] >= enforce_end:

                print("Found a valid time segment")

                return 2

            elif result == results['change_models'][-1]:

                return 1

            else:

                continue
