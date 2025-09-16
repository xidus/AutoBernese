"""
Command-line interface for data sources

"""

import typing as t
import itertools as it
import logging

import click
from click_aliases import ClickAliasedGroup
from rich import print

from ab.cli import (
    _input,
    _filter,
    _options,
    _actions,
)
from ab import configuration
from ab.configuration import sources as _sources
from ab.bsw import campaign as _campaign
from ab.data import (
    TransferStatus,
    ftp as _ftp,
    http as _http,
    file as _file,
)


log = logging.getLogger(__name__)


"""
*   The source definition should know what module to use as download agent and
    provide this.
*   A source definition is like a mother to the individual source/destination
    pairs in that they each are provided a reference to an instance of the
    download agent that is setup for the host location.
*   Once set up, a download agent (local or FTP or HTTP of SFTP) provides the
    following interface: *   A connection method that establishes the connection
    and re-news it, if it is down.
        *   This could be a context manager (with agent as connection/session:)
    *   The connection/session has an obtain method which takes the source and
        destination location as input and uses the connection to the source host
        to send a request to that host.
*   A request is a wrapper distinct to the connection type so that it makes the
    right commands that make the transfer possible..._ *   HTTP should just have
    a GET request, and use requests as library *   FTP should have a renewable
    session and function the same as before, but only taking a single
    source/destination pair. (What about wildcard-resolution?)
        *   Can FTP be done as batch?
        *   And can a single GET command use wildcards?

Questions:

*   Where are the interfaces? *   Agent == Module? as in agent = http.py?

Outstanding requirements:

*   How to batch download through FTP.
*   How to keep the existing functionality that only non-existing (dataclass
    SourceArguments: Age: int = math.inf)

Concept:

*   Configuration

    *   Layer: I/O

    *   Reads list of sources and creates a Source

Definition for each

*   Source definition

    *   Corresponds to Task Definition

*   Agent

    *   Corresponds to Task

    *   act()

        *   Corresponds to a runner...

        *   Runs the function that actually transfers data, based on keywords
            stored in the Agent.

*   The Source returns agent instances that each perform a single transfer,
    unless it is a batch situation.


*   The agent has a filecheck interface:

    *   Check source (ifname) exists... (or this is only evident, when the
        tranfer is tried...), so the information should be returned by the agent
        as a not-found-status and the I/O layer can deal with this (log it and
        continue on with the next file source destination paur.)



"""


"""
Commands (source (src))

*   download (dl)
*   ls
*   ls -v (show rendered)

"""


def get_configuration(name: str | None = None) -> dict[str, t.Any]:
    if name is not None:
        log.info(f"Using campaign configuration from {name} ...")
        return _campaign.load(name)
    log.info(f"Using default configuration ...")
    return configuration.load()


def print_and_log(msg: str, level: str) -> None:
    print(msg)
    log = logging.getLogger(__name__)
    if not hasattr(log, level):
        raise RuntimeError(f"No such log level: {level!r} ...")
    getattr(log, level)(msg)


@click.command
@_options.identifiers
@_options.exclude
@_options.campaign
@_options.verbose
def ls(
    identifiers: list[str] | None,
    exclude: list[str] | None = None,
    name: str | None = None,
    verbose: bool = False,
) -> None:
    """
    List sources in common or campaign-specific configuration.

    """
    print(f"TODO: Print list of tasks ({verbose=}) ...")


@click.command
@_options.identifiers
@_options.exclude
@_options.force
@_options.campaign
@_options.yes
def obtain(
    identifiers: list[str] | None,
    exclude: list[str] | None = None,
    force: bool = False,
    name: str | None = None,
    yes: bool = False,
) -> None:
    """
    Obtain sources and put them at the desired destination.

    """
    config = get_configuration(name)
    raw_sources = _filter.get_raw(config, "sources", identifiers, exclude)

    if not raw_sources:
        print_and_log(f"No sources matching selected identifiers ...", "debug")
        return

    # Build instances
    task_definitions = _sources.load_all_as_task_definitions(raw_sources)

    # Preamble
    print("Downloading the following sources")
    for task_definition in task_definitions:
        print(
            task_definition.identifier,
            task_definition.description,
            len(task_definition.tasks),
        )

    # Ask to proceed or not
    if not _input.prompt_proceed():
        raise SystemExit

    shorthand = {td.identifier: td.tasks for td in task_definitions}
    for td in task_definitions:
        _actions.run_tasks(td.tasks)
    log.info("Finished downloading sources ...")
