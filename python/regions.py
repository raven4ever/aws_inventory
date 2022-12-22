import boto3

ssm = boto3.client('ssm')


class Region:
    def __init__(self, short_name) -> None:
        self.short_name = short_name
        self.long_name = self._get_region_long_name()

    def __repr__(self) -> str:
        return f'{self.short_name} - {self.long_name}'

    def _get_region_long_name(self) -> str:
        param_name = (
            '/aws/service/global-infrastructure/regions/'
            f'{self.short_name}/longName'
        )
        response = ssm.get_parameters(
            Names=[param_name]
        )
        return response['Parameters'][0]['Value']


class Regions:
    @classmethod
    def get_available_regions(cls) -> set():
        output = set()

        for page in ssm.get_paginator('get_parameters_by_path').paginate(
            Path='/aws/service/global-infrastructure/regions'
        ):
            output.update(Region(p['Value']) for p in page['Parameters'])

        return output
