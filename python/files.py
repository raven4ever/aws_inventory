import os
from typing import List

from dataclass_csv import DataclassWriter

from commons import ReportEntry
from handlers.dbs import DBReportEntry
from handlers.ec2 import EC2ReportEntry
from handlers.elb import LBReportEntry
from handlers.s3 import S3ReportEntry

SERVICE_TO_REPORT_MAP = {
    'ec2': EC2ReportEntry,
    'elb': LBReportEntry,
    'dbs': DBReportEntry,
    's3': S3ReportEntry
}


def init_save_files(path: str) -> None:
    print(f'Initializing reports to {path}')

    for service in SERVICE_TO_REPORT_MAP:
        with open(os.path.join(path, f'{service}.csv'), 'a') as file:
            w = DataclassWriter(
                file, [], SERVICE_TO_REPORT_MAP[service])
            w.write()


def write_data_to_file(path: str, service: str, data: List[ReportEntry]) -> None:
    with open(os.path.join(path, f'{service}.csv'), 'a') as file:
        w = DataclassWriter(
            file, data, SERVICE_TO_REPORT_MAP[service])
        w.write(skip_header=True)
