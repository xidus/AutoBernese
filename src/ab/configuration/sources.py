"""
Configuration tools to build Source instances as well as TaskDefinition
instances from source entries.

"""

from typing import Any

from ab.configuration import SectionListItemType
from ab.data.source import Source
from ab.tasks import TaskDefinition


def load(kwargs: SectionListItemType) -> Source:
    return Source(**kwargs)


def load_all(raw: list[SectionListItemType]) -> list[Source]:
    return [load(kwargs) for kwargs in raw]


def convert_kwargs_source_to_task_definition(
    kwargs: SectionListItemType,
) -> SectionListItemType:
    """

    Convert:

    - identifier: TEST
      description: TEST
      url: https://example.com/
      filenames:
      - [filename_input_{station}.ext, '{station}/filename_output_{station}.ext']
      destination: /tmp/autobernese
      parameters:
        station: [station1]

    to:

    - identifier: TEST
      description: TEST
      run: TransferFiles
      arguments:
        url: https://example.com/
        filenames:
        - [filename_input_{station}.ext, '{station}/filename_output_{station}.ext']
        destination: /tmp/autobernese
      parameters:
        station: [station1]

    """
    keys = ("url", "filenames", "destination")
    arguments = {key: kwargs.get(key) for key in keys}
    [kwargs.pop(key) for key in keys]

    # Popping this to make it appear in the right order below
    parameters = kwargs.pop("parameters")

    # Create a new dict with the popped arguments (except parameters)
    update = dict(arguments=arguments, parameters=parameters)
    return {**kwargs, **update}


def load_as_task_definition(kwargs: SectionListItemType) -> TaskDefinition:
    kwargs_transformed = convert_kwargs_source_to_task_definition(kwargs)
    return TaskDefinition(**kwargs_transformed)


def load_all_as_task_definitions(
    raw: list[SectionListItemType],
) -> list[TaskDefinition]:
    return [load_as_task_definition(kwargs) for kwargs in raw]
