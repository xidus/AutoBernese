"""
Transfer files over FTP

"""

import datetime as dt
from pathlib import Path
from ftplib import FTP
from fnmatch import fnmatch
from ftplib import (
    FTP,
    error_perm,
)
from collections.abc import Iterator
from contextlib import contextmanager
import functools
import logging

from ab.data import TransferStatus
from ab.data.source import RemoteLocalPair
from ab.data.stats import file_age


log = logging.getLogger(__name__)


@contextmanager
def specific_path(ftp: FTP, path: str) -> Iterator[FTP]:
    cwd = ftp.pwd()
    log.debug(f"switch to {path} ...")
    ftp.cwd(path)
    try:
        yield ftp
    finally:
        log.debug(f" -> switch back to {cwd} ...")
        ftp.cwd(cwd)


def list_files(ftp: FTP, path: str, *, ix_column: int = 8) -> list[str]:
    """
    List files without looking for a cached version.

    Note: Not all the servers that we access support the newer MLSD command, so
    we rely on the older NLST command.

    Works for non-Windows FTP-servers, where the directory listing is what you
    get with `ls`.

    """
    with specific_path(ftp, path) as tmp:
        tmp.retrlines("LIST", (lines := []).append)  # type: ignore
        return [line.split()[ix_column] for line in lines if not line.startswith("d")]


def download(pair: RemoteLocalPair) -> TransferStatus:
    """
    Download remote file(s) to local destination

    Logic:

    *   If the filename does not contain wildcards to match against the remote
        directory listing, simply, download the file.

    *   Otherwise, the filename, which we then know contains wildcards, is
        matched against the list of files inside the remote parent directory to
        get all possible files to download based on the given pattern.

    Note:

    *   The assumption for a RemoteLocalPair instance is that the remote path in
        `path_remote` is a directory in which to find the file denoted `fname`.

        For now, the algorithm does not look inside any directory.

    """
    status = TransferStatus()

    # Log on to the host, immediately, as we need to probe for files directories
    ftp = FTP(pair.host)
    ftp.login()

    try:

        # TODO: Check that wildcard remote fname && no ofname given (since this is ambiguous)
        if "*" not in pair.fname:
            # If the filename has no wildcard, just download the file
            candidates = [pair.fname]
            destinations = [Path(pair.path_local) / pair.fname]

        else:
            # Get files that match the current source filename
            log.debug("Searching for wildcard results")
            listed = list_files(ftp, pair.path_remote)
            candidates = fnmatch.filter(listed, pair.fname)
            if not candidates:
                fname_remote = f"{pair.path_remote}/{pair.fname}"
                log.info(f"No files matching {fname_remote} ...")
                status.not_found = 1
                return status
            destinations = [
                Path(pair.path_local) / candidate for candidate in candidates
            ]

        # Remove candidates, if local file exist and not too old
        to_download = [
            (fname, ofname)
            for (fname, ofname) in zip(candidates, destinations)
            if file_age(ofname) <= pair.max_age
        ]

        # Finally, download each of the filenames resolved
        ftp.cwd(pair.path_remote)
        for fname, ofname in to_download:
            ofname.parent.mkdir(parents=True, exist_ok=True)
            log.info(f"Downloading {fname} ...")
            try:
                with open(ofname, "wb") as f:
                    ftp.retrbinary(f"RETR {fname}", f.write)

            except error_perm as e:
                log.warn(f"Filename {fname} could not be downloaded ...")
                log.debug(f"{e}")

                # NOTE
                log.info(f"Deleting empty or incomplete {ofname} ...")
                ofname.unlink()

                status.failed += 1

                continue

            status.success += 1

    except KeyboardInterrupt:
        log.info(f"Interrupted by user. Closing FTP connection ...")
        ftp.close()
        raise

    return status
