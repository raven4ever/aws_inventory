import os
from dataclasses import dataclass


def logs_type(string):
    if string.upper() in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        return string.upper()
    else:
        raise ValueError(string)


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


@dataclass(frozen=True)
class ReportEntry:
    region: str
    service: str
    sub_service: str
    resource_id: str


@dataclass
class Report:
    region: str
