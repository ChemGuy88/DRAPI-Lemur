"""
Copy files to a single destination directory. Optionally this directory can be added to a compressed archive.
"""

import logging
import os
import pprint
import shutil
import zipfile
from pathlib import Path
from typing_extensions import List
# First-party packages
from drapi.code.drapi.drapi import (getTimestamp,
                                    makeDirPath,
                                    successiveParents)


def gather_files(destination_folder: str,
                 list_of_directories: List[str],
                 list_of_files: List[List[str]],  # NOTE TODO Not implemented yet.
                 list_of_directories_new_names: List[str],
                 logger: logging.Logger,
                 list_of_loose_files: List[str] = [],
                 timestamp: str = getTimestamp(),
                 overwrite_if_exists_archive: bool = False,
                 overwrite_if_exists_file: bool = False,
                 overwrite_if_exists_folder: bool = False,
                 create_merged_folder: bool = False,
                 create_compressed_archive: bool = True,
                 delete_folder_after_archiving: bool = False):
    """
    Copy files to a single destination directory. Optionally this directory can be added to a compressed archive.
    """
    print(locals())
    arguments_list_as_string = pprint.pformat(locals())
    logger.info(f""" >>> List of arguments >>>
{arguments_list_as_string}
<<< List of arguments <<<""")
    # Define the destination path
    destinationRootFolder = Path(destination_folder)

    # Define archive root folder name NOTE This is useful because if you use the default behavior of `unzip` it would unzip all the portions individually in the current working directory. By using this archive root folder, if the user uses the default behavior, all the portions, including any loose files, are extracted into a single directory.
    archive_root_folder_name = f"IDR Data Release - {timestamp}"

    # Copy files and directories
    if create_merged_folder:
        if destinationRootFolder.exists():
            logger.warning(f"""WARNING: The destination folder already exists: "{destinationRootFolder.absolute()}".""")
            if overwrite_if_exists_folder:
                logger.info("""  Removing folder contents to make room for new files.""")
                for fpath in destinationRootFolder.iterdir():
                    logger.info(f"""    Removing "{fpath.absolute()}".""")
                    os.remove(fpath)
                    logger.info(f"""    Removing "{fpath.absolute()}" - done.""")
            else:
                msg = "  The destination folder exists and no option was passed to over-write it."
                logger.critical(msg)
                raise Exception(msg)
        else:
            logger.info(f"""Making destination folder: "{destinationRootFolder.absolute()}".""")
            makeDirPath(destinationRootFolder)

        logger.info("""Working on list of files.""")
        for fpathString in list_of_loose_files:
            fpath = Path(fpathString)
            logger.info(f"""  Working on file "{fpath.absolute()}".""")
            dest = destinationRootFolder.joinpath(fpath.name)
            logger.info(f"""    Saving to "{dest.absolute()}".""")
            shutil.copyfile(fpath, dest)
        logger.info("""Working on list of files - done.""")

        logger.info("""Working on list of directories.""")
        if list_of_directories_new_names:
            listOfDirectoriesNewNames = list_of_directories_new_names[:]
        else:
            listOfDirectoriesNewNames = ["" for _ in list_of_directories]
        directoryPathsAndNames = zip(list_of_directories, listOfDirectoriesNewNames)
        for directoryString, newDirectoryName in directoryPathsAndNames:
            directory = Path(directoryString)
            destinationFolder = destinationRootFolder.joinpath(newDirectoryName)
            destinationFolder.mkdir()
            listOfFiles1 = sorted(list(directory.iterdir()))
            for fpath in listOfFiles1:
                logger.info(f"""  Working on file "{fpath.absolute()}".""")
                dest = destinationFolder.joinpath(fpath.name)
                logger.info(f"""    The destination path is "{dest.absolute()}".""")
                if dest.exists():
                    msg = f"""    WARNING: This file already exists: "{dest}"."""
                    logger.warning(msg)
                    if overwrite_if_exists_file:
                        continueOperation = True
                    else:
                        continueOperation = False
                else:
                    continueOperation = True
                if continueOperation:
                    logger.info("""    Saving to destination path.""")
                    shutil.copyfile(fpath, dest)
                else:
                    logger.info("""    The file was not saved to the destination path. File over-write is set to `False`.""")
        logger.info("""Working on list of directories - done.""")

    # Create compressed archive
    if create_compressed_archive:
        archivePath = destinationRootFolder.with_suffix(".ZIP")
        logger.info(f"""Creating compressed archive: "{archivePath.absolute()}"".""")
        archivePathParentDir, _ = successiveParents(pathObj=archivePath,
                                    numLevels=1)
        if overwrite_if_exists_archive:
            if archivePath.exists():
                logger.info("""The archive folder already exists and will be removed before writing.""")
                os.remove(archivePath)

        # Define list of files to archive, and their paths
        if list_of_directories_new_names:
            listOfDirectoriesNewNames = list_of_directories_new_names[:]
        else:
            listOfDirectoriesNewNames = ["" for _ in list_of_directories]
        directoryPathsAndNames = zip(list_of_directories, listOfDirectoriesNewNames)
        listOfFiles2All = []
        for directoryString, newDirectoryName in directoryPathsAndNames:
            directory = Path(directoryString)
            listOfFiles2 = sorted(list(directory.iterdir()))
            for fpath2 in listOfFiles2:
                dest2 = Path(archive_root_folder_name).joinpath(newDirectoryName, fpath2.name)
                listOfFiles2All.append((fpath2, dest2))
        
        logger.info(f"""These are the files paths for the archived items:\n{pprint.pformat(listOfFiles2All)}.""")

        with zipfile.ZipFile(file=archivePath,
                             mode="a",
                             compression=zipfile.ZIP_DEFLATED) as zipObj:
            logger.info("Adding files to archive.")
            for fpath2, dest2 in sorted(listOfFiles2All):
                logger.info(f"""  Working on file "{fpath2.absolute()}".""")
                logger.info(f"""    This has a destination path of "{dest2}".""")
                zipObj.write(filename=fpath2, arcname=dest2)
        logger.info("Creating compressed archive - done.")

        if create_merged_folder:
            if delete_folder_after_archiving:
                logger.info("""Removing intermediate folder.""")
                shutil.rmtree(destinationRootFolder)
                logger.info("""Removing intermediate folder - done.""")
            else:
                pass
