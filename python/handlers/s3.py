from dataclasses import dataclass, field
from typing import List

import boto3
from botocore.exceptions import ClientError, SSLError

from commons import Report, ReportEntry


@dataclass(frozen=True)
class S3ReportEntry(ReportEntry):

    def __iter__(self):
        yield self.region
        yield self.service
        yield self.sub_service
        yield self.resource_id


@dataclass
class S3Report(Report):
    s3_service_report: List[S3ReportEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.s3 = boto3.resource('s3', region_name=self.region)
        self.create_service_report()

    def create_service_report(self) -> None:
        try:
            self.s3_service_report.extend(self.get_s3_buckets())
        except ClientError:
            print(f'Skipping S3 service for region {self.region}...')
        except SSLError:
            print(f'S3 service SSL error for region {self.region}...')

    def get_s3_buckets(self) -> List[S3ReportEntry]:
        s3_entries: List[S3ReportEntry] = list()
        all_instances = self.s3.buckets.all()

        for bucket in all_instances:
            s3_entries.append(S3ReportEntry(
                region=self.region,
                service='S3',
                sub_service='S3',
                resource_id=bucket.name))

        return s3_entries
