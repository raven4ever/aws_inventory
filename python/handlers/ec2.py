from dataclasses import dataclass, field
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError, SSLError

from common import Report, ReportEntry


@dataclass
class EC2ReportEntry(ReportEntry):
    availability_zone: Optional[str] = 'N/A'
    instance_type: Optional[str] = 'N/A'

    def __iter__(self):
        yield self.region
        yield self.service
        yield self.sub_service
        yield self.resource_id
        yield self.availability_zone
        yield self.instance_type


@dataclass
class EC2Report(Report):
    ec2_service_report: List[EC2ReportEntry] = field(default_factory=list)

    def __post_init__(self):
        self.ec2 = boto3.resource('ec2', region_name=self.region)
        self.create_service_report()

    def create_service_report(self) -> None:
        try:
            self.ec2_service_report.extend(self.get_ec2_instances())
            self.ec2_service_report.extend(self.get_ebs_instances())
            self.ec2_service_report.extend(self.get_amis())
            self.ec2_service_report.extend(self.get_ec2_snapshots())
        except ClientError:
            print(f'Skipping EC2 for region {self.region}...')
        except SSLError:
            print(f'EC2 SSL error for region {self.region}...')

    def get_amis(self) -> List[EC2ReportEntry]:
        ami_entries: List[EC2ReportEntry] = list()
        all_amis = list(self.ec2.images.filter(Owners=['self']))

        for ami in all_amis:
            ami_entries.append(EC2ReportEntry(
                region=self.region,
                service='EC2',
                sub_service='AMI',
                resource_id=ami.id))

        return ami_entries

    def get_ec2_snapshots(self) -> List[EC2ReportEntry]:
        snap_entries: List[EC2ReportEntry] = list()
        all_snap = list(self.ec2.snapshots.filter(OwnerIds=['self']))

        for snap in all_snap:
            snap_entries.append(EC2ReportEntry(
                region=self.region,
                service='EC2',
                sub_service='Snapshot',
                resource_id=snap.snapshot_id))

        return snap_entries

    def get_ebs_instances(self) -> List[EC2ReportEntry]:
        ebs_entries: List[EC2ReportEntry] = list()
        all_ebs = self.ec2.volumes.all()

        for volume in all_ebs:
            ebs_entries.append(EC2ReportEntry(
                region=self.region,
                service='EC2',
                sub_service='EBS',
                resource_id=volume.id,
                availability_zone=volume.availability_zone))

        return ebs_entries

    def get_ec2_instances(self) -> List[EC2ReportEntry]:
        ec2_entries: List[EC2ReportEntry] = list()
        all_instances = self.ec2.instances.all()

        for instance in all_instances:
            ec2_entries.append(EC2ReportEntry(
                region=self.region,
                service='EC2',
                sub_service='EC2',
                resource_id=instance.instance_id,
                instance_type=instance.instance_type,
                availability_zone=instance.placement['AvailabilityZone']))

        return ec2_entries
