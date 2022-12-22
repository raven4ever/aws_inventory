import os
import sys
from argparse import ArgumentParser

from commons import dir_path
from handlers.ec2 import EC2Report, EC2ReportEntry
from regions import Regions
from handlers.elb import LBReport, LBReportEntry
from dataclass_csv import DataclassWriter

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

            if len(ec2_region_report) > 0:
                with open(os.path.join(REPORTS_PATH, 'ec2.csv'), 'a') as ec2_file:
                    w = DataclassWriter(
                        ec2_file, ec2_region_report, EC2ReportEntry)
                    w.write()

            lb_region_report = LBReport(
                region=region.short_name).elb_service_report

            if len(lb_region_report) > 0:
                with open(os.path.join(REPORTS_PATH, 'elb.csv'), 'a') as elb_file:
                    w = DataclassWriter(
                        elb_file, lb_region_report, LBReportEntry)
                    w.write()
    else:
        print('just watching, no saving')
