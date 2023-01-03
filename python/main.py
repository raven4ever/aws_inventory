import logging
import sys
from argparse import ArgumentParser

from commons import dir_path, logs_type
from config import Configuration
from files import init_save_files, write_data_to_file
from handlers.dbs import DBReport
from handlers.ec2 import EC2Report
from handlers.elb import LBReport
from handlers.s3 import S3Report

REPORTS_PATH = '.'

if __name__ == '__main__':
    # read the reports dir
    parser = ArgumentParser(
        description='Detect AWS Infrastructure resources')
    parser.add_argument(
        '--report', required=False, type=dir_path, help='Path to the folder where to store the services reports.')
    parser.add_argument(
        '--log', required=False, type=logs_type, help='Logs level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    args = parser.parse_args()

    REPORTS_PATH = getattr(args, 'report')
    LOG_LEVEL = getattr(args, 'log')

    logging.basicConfig(level=LOG_LEVEL)

    logging.info('Get available regions...')

    app_config = Configuration()
    all_regions = app_config.regions

    if len(all_regions) == 0:
        logging.error('You might have a connectivity problem!')
        sys.exit(1)

    if REPORTS_PATH:
        init_save_files(REPORTS_PATH)

        for region in all_regions:
            logging.info(f'Getting information about the {region} region')

            ec2_region_report = EC2Report(
                region=region.short_name).ec2_service_report

            if len(ec2_region_report) > 0:
                write_data_to_file(REPORTS_PATH, 'ec2', ec2_region_report)

            lb_region_report = LBReport(
                region=region.short_name).elb_service_report

            if len(lb_region_report) > 0:
                write_data_to_file(REPORTS_PATH, 'elb', lb_region_report)

            db_region_report = DBReport(
                region=region.short_name).db_service_report

            if len(db_region_report) > 0:
                write_data_to_file(REPORTS_PATH, 'dbs', db_region_report)

            s3_region_report = S3Report(
                region=region.short_name).s3_service_report

            if len(s3_region_report) > 0:
                write_data_to_file(REPORTS_PATH, 's3', s3_region_report)
    else:
        print('just watching, no saving')
