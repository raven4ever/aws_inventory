from dataclasses import dataclass, field
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError, SSLError

from commons import Report, ReportEntry


@dataclass(frozen=True)
class DBReportEntry(ReportEntry):
    availability_zone: Optional[str] = 'N/A'
    instance_type: Optional[str] = 'N/A'
    engine: Optional[str] = 'N/A'

    def __iter__(self):
        yield self.region
        yield self.service
        yield self.sub_service
        yield self.resource_id
        yield self.availability_zone
        yield self.instance_type
        yield self.engine


@dataclass
class DBReport(Report):
    db_service_report: List[DBReportEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.rds = boto3.client('rds', region_name=self.region)
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.docdb = boto3.client('docdb', region_name=self.region)

        self.create_service_report()

    def create_service_report(self) -> None:
        try:
            self.db_service_report.extend(self.get_rds_instances())
            self.db_service_report.extend(self.get_dynamodb_tables())
            self.db_service_report.extend(self.get_documentdb_instances())
        except ClientError:
            print(f'Skipping RDS service for region {self.region}...')
        except SSLError:
            print(f'RDS service SSL error for region {self.region}...')

    def get_rds_instances(self) -> List[DBReportEntry]:
        dbs: List[DBReportEntry] = list()
        response = self.rds.describe_db_instances()

        for instance in response['DBInstances']:
            dbs.append(DBReportEntry(
                region=self.region,
                service='DB',
                sub_service='RDS',
                resource_id=instance['DBInstanceIdentifier'],
                availability_zone=instance['AvailabilityZone'],
                instance_type=instance['DBInstanceClass'],
                engine=instance['Engine']
            ))

        return dbs

    def get_dynamodb_tables(self) -> List[DBReportEntry]:
        dbs: List[DBReportEntry] = list()
        response = self.dynamodb.tables.all()

        for table in response:
            dbs.append(DBReportEntry(
                region=self.region,
                service='DB',
                sub_service='DynamoDB',
                resource_id=table.name,
                engine='DynamoDB'
            ))

        return dbs

    def get_documentdb_instances(self) -> List[DBReportEntry]:
        dbs: List[DBReportEntry] = list()
        response = self.rds.describe_db_instances()

        for instance in response['DBInstances']:
            dbs.append(DBReportEntry(
                region=self.region,
                service='DB',
                sub_service='DocumentDB',
                resource_id=instance['DBInstanceIdentifier'],
                availability_zone=instance['AvailabilityZone'],
                instance_type=instance['DBInstanceClass'],
                engine=instance['Engine']
            ))

        return dbs
