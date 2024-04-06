"""
Function(s) to modify clinical text output TSV to the right format for processing in the SDOH pipeline.
"""

import logging
from pathlib import Path
from typing import (Literal,
                    Union)
# Third-party packages
import pandas as pd


def modifyTSV(fpath: Union[str, Path],
              toDirectory: Union[str, Path],
              idColumnName: str = "LinkageNoteID"):
    """
    Modifies notes text TSV files in preparation for analysis in the SDOH pipeline.
    Modifications:
        - Adds two dummy columns
            - "CNTCT_NUM" with value "0"
            - "NOTE_KEY" with value "123456789"
        - Re-orders the columns
        - Renames the clinical text ID column from `idColumnName` to "NOTE_ENCNTR_KEY"
    """
    runOutputDir = Path(toDirectory)

    # Read file
    df = pd.read_csv(fpath, delimiter="\t")

    # Set dummy values
    df["CNTCT_NUM"] = 0
    df["NOTE_KEY"] = 123456789

    # Re-order columns
    df = df[[idColumnName,
             "NOTE_KEY",
             "CNTCT_NUM",
             "note_text"]]
    
    # Rename columns
    df = df.rename(columns={idColumnName: "NOTE_ENCNTR_KEY"})

    # Save modified TSV file
    fname = fpath.name
    savePath = runOutputDir.joinpath(fname)
    df.to_csv(savePath, index=False, sep="\t")


def wrapModify(fpath: Path,
               textType: Literal["note", "order"],
               toDirectory: Union[Path, str],
               logger: logging.Logger):
    """
    A wrapper function for `modifyTSV` to be called in parallel work.
    """
    logger.info(f"""  Working on path "{fpath}".""")
    if textType == "note":
        if "deid" in fpath.name:
            modifyTSV(fpath=fpath,
                    toDirectory=toDirectory,
                    idColumnName="deid_link_note_id")
        else:
            modifyTSV(fpath=fpath,
                    toDirectory=toDirectory,
                    idColumnName="LinkageNoteID")
    elif textType == "order":
        if "deid" in fpath.name:
            modifyTSV(fpath=fpath,
                    toDirectory=toDirectory,
                    idColumnName="deid_order_id")
        else:
            modifyTSV(fpath=fpath,
                    toDirectory=toDirectory,
                    idColumnName="OrderKey")
    else:
        raise Exception(f"""Expected `textType` to be one of "note" or "order", but got "{textType}" instead.""")
    logger.info(f"""  Working on path "{fpath}" - done.""")
