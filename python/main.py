import csv
import os
import sys
from argparse import ArgumentParser

from commons import dir_path
from handlers.ec2 import EC2Report
from regions import Regions
from handlers.elb import LBReport

REPORTS_PATH = '.'

if __name__ == '__main__':
    # read the reports dir
    parser = ArgumentParser(
        description='Detect AWS Infrastructure resources')
    parser.add_argument(
        '--report', required=False, type=dir_path, help='Path to the folder where to store the services reports.')

    args = parser.parse_args()

    REPORTS_PATH = getattr(args, 'report')

    print('Get available regions...')

    all_regions = Regions.get_all_regions()

    if len(all_regions) == 0:
        print('You might have a connectivity problem!')
        sys.exit(1)

    if REPORTS_PATH:
        print(f'Saving reports to {REPORTS_PATH}')
        for region in all_regions:
            print(f'Getting information about the {region} region')
            ec2_region_report = EC2Report(
                region=region.short_name).ec2_service_report

            with open(os.path.join(REPORTS_PATH, 'ec2.csv'), 'a') as ec2_file:
                writer = csv.writer(ec2_file)
                writer.writerows(ec2_region_report)

            lb_region_report = LBReport(
                region=region.short_name).elb_service_report

            with open(os.path.join(REPORTS_PATH, 'elb.csv'), 'a') as elb_file:
                writer = csv.writer(elb_file)
                writer.writerows(lb_region_report)
    else:
        print('just watching, no saving')
