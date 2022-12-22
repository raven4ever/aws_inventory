import os
from dataclasses import dataclass


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


@dataclass
class ReportEntry:
    region: str
    service: str
    sub_service: str
    resource_id: str


@dataclass
class Report:
    region: str
