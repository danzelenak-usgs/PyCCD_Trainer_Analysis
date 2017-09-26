import argparse
from analyze_pyccd_training_data import CheckTrainingData
from analyze_pyccd_training_data import CheckTimeSegments

parser = argparse.ArgumentParser()

parser.add_argument('-hv', nargs=2, type=int, required=True, metavar=('HH', 'VV'),
                    help='Horizontal and vertical ARD grid identifiers')

parser.add_argument('-t', '--trends', type=str, required=False,
                    help='Path to the CONUS Trends Land Cover year 2000 .tif file')

parser.add_argument('-o', '--outdir', type=str, required=True,
                    help='Path to where subfolders and output files will be saved '
                         '(currently chip-subset Trends and Trends+Time Segment Chip Masks)')

parser.add_argument('-j', '--jsondir', type=str, required=True,
                    help='Path to the location of json files containing the PyCCD results for the current tile')

args = parser.parse_args()

# h5v2 = CheckTrainingData()

# h5v2.analyze_chips()

if args.trends:

    check_training_data = CheckTrainingData(h=args.hv[0], v=args.hv[1], in_trends=args.trends,
                                            out_dir=args.outdir, json_dir=args.jsondir)

    check_training_data.analyze_chips()

else:

    check_time_segments = CheckTimeSegments(h=args.hv[0], v=args.hv[1], json_dir=args.jsondir, out_dir=args.outdir)

    check_time_segments.analyze_time_segments()
