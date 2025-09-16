"""
Configuration models

"""

import typing as t
from pathlib import Path
import datetime as dt

# from dataclasses import (
#     dataclass,
#     field,
# )

from pydantic import BaseModel

from ab.bsw.campaign import MetaData
from ab.tasks import TaskDefinition
from ab.data.source import Source


# @dataclass
class BSWEnvironment(BaseModel):
    C: str
    DOC: str
    PAN: str
    MODEL: str
    CONFIG: str
    D: str
    P: str
    S: str
    U: str
    T: str


# @dataclass
class BSWFiles(BaseModel):
    release_info: str | Path
    campaign_menu: str | Path


# @dataclass
class Logging(BaseModel):
    pass


# @dataclass
class Runtime(BaseModel):
    ab: str | Path
    logging: Logging
    campaign_templates: str | Path
    common_config: str | Path
    sections_to_override: list[str]


# @dataclass
class CampaignDirectory(BaseModel):
    name: str
    files: list[str | Path]  # = field(default_factory=list)


# @dataclass
class Troposphere(BaseModel):
    ipath: str | Path
    opath: str | Path
    ifname: str
    ofname: str
    beg: dt.date | dt.datetime
    end: dt.date | dt.datetime


# @dataclass
class EnvironmentSetting(BaseModel):
    variable: str
    value: str


# @dataclass
class Configuration(BaseModel):
    """
    Base class for configuration data

    """


# @dataclass
class SectionsOverwritable(BaseModel):
    campaign: list[CampaignDirectory] | None = None
    troposphere: Troposphere | None = None
    sources: list[Source] | None = None


# @dataclass
class CoreConfiguration(Configuration):
    bsw_env: BSWEnvironment
    bsw_files: BSWFiles
    env: str | Path
    runtime: Runtime


# @dataclass
class CampaignConfiguration(Configuration):
    metadata: MetaData | None = None
    environment: list[EnvironmentSetting] | None = None
    tasks: list[TaskDefinition] | None = None
    # Set repr to False to avoid lookup raising a RuntimeError, when not set
    clean: list[str] | None = None
