import logging
from dataclasses import dataclass, field
from typing import List

import boto3
from botocore.exceptions import ClientError, SSLError

from commons import Report, ReportEntry


@dataclass(frozen=True)
class LBReportEntry(ReportEntry):

    def __iter__(self):
        yield self.region
        yield self.service
        yield self.sub_service
        yield self.resource_id


@dataclass
class LBReport(Report):
    elb_service_report: List[LBReportEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.elbv2 = boto3.client('elbv2', region_name=self.region)
        self.create_service_report()

    def create_service_report(self) -> None:
        try:
            self.elb_service_report.extend(self.get_lbs())
        except ClientError as ce:
            logging.error(ce)
            logging.error(f'Skipping LB service for region {self.region}...')
        except SSLError as ssle:
            logging.error(ssle)
            logging.error(f'LB service SSL error for region {self.region}...')

    def get_lbs(self) -> List[LBReportEntry]:
        lbs: List[LBReportEntry] = list()
        response = self.elbv2.describe_load_balancers()

        for instance in response['LoadBalancers']:
            lbs.append(LBReportEntry(
                region=self.region,
                service='ELB',
                sub_service=instance['Type'],
                resource_id=instance['LoadBalancerName']
            ))

        return lbs
