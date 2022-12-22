from dataclasses import dataclass
from typing import Set

import boto3

ssm = boto3.client('ssm')


@dataclass(frozen=True)
class Region:
    short_name: str
    long_name: str


class Regions:
    @classmethod
    def get_all_regions(cls) -> Set[Region]:
        output: Set[Region] = set()

        for page in ssm.get_paginator('get_parameters_by_path').paginate(
            Path='/aws/service/global-infrastructure/regions'
        ):
            for p in page['Parameters']:
                short_name = p['Value']
                long_name_param = (
                    '/aws/service/global-infrastructure/regions/'
                    f'{short_name}/longName'
                )
                response = ssm.get_parameters(
                    Names=[long_name_param]
                )

                output.add(Region(short_name=short_name,
                                  long_name=response['Parameters'][0]['Value']))

        return output
