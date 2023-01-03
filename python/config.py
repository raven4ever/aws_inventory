
from dataclasses import dataclass
from pathlib import Path
from typing import Set

import boto3
import yaml


@dataclass(frozen=True)
class Region:
    short_name: str
    long_name: str


class Configuration:
    def __init__(self) -> None:
        self.ssm = boto3.client('ssm')

        config_file_path = Path('config.yml')

        if config_file_path.is_file():
            self.configuration = self.read_config_file(config_file_path)

            config_regions = self.read_config_file_regions()

            if len(config_regions) > 0:
                self.regions = config_regions
            else:
                print('Using all regions')
                self.regions = self.get_all_regions()
        else:
            print('Using all regions')
            self.regions = self.get_all_regions()

    def read_config_file(self, config_file_path: Path) -> dict:
        with open(config_file_path.absolute()) as file:
            config_file = yaml.full_load(file)
        return config_file

    def read_config_file_regions(self) -> Set[Region]:
        output: Set[Region] = set()

        if 'regions' in self.configuration:
            for short_name in self.configuration['regions']:
                output.add(Region(short_name=short_name,
                                  long_name=self.get_region_long_name(short_name)))

        return output

    def get_all_regions(self) -> Set[Region]:
        output: Set[Region] = set()

        for page in self.ssm.get_paginator('get_parameters_by_path').paginate(
            Path='/aws/service/global-infrastructure/regions'
        ):
            for p in page['Parameters']:
                short_name = p['Value']

                output.add(Region(short_name=short_name,
                                  long_name=self.get_region_long_name(short_name)))

        return output

    def get_region_long_name(self, short_name: str) -> str:
        long_name_param = (
            '/aws/service/global-infrastructure/regions/'
            f'{short_name}/longName'
        )
        response = self.ssm.get_parameters(
            Names=[long_name_param]
        )

        return response['Parameters'][0]['Value']
