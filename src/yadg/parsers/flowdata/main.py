import logging
import json
from pydantic import BaseModel
from . import drycal

logger = logging.getLogger(__name__)


def process(
    fn: str,
    encoding: str = "utf-8",
    timezone: str = "localtime",
    parameters: BaseModel = None,
) -> tuple[list, dict, bool]:
    """
    Flow meter data processor

    This parser processes flow meter data.

    Parameters
    ----------
    fn
        File to process

    encoding
        Encoding of ``fn``, by default "utf-8".

    timezone
        A string description of the timezone. Default is "localtime".

    filetype
        Whether a rtf, csv, or txt file is to be expected. When `None`, the suffix of
        the file is used to determine the file type.

    convert
        Specification for column conversion. The `key` of each entry will form a new
        datapoint in the ``"derived"`` :class:`(dict)` of a timestep. The elements within
        each entry must either be one of the ``"header"`` fields, or ``"unit"`` :class:`(str)`
        specification. See processing convert for more info.

    calfile
        ``convert``-like functionality specified in a json file.

    date
        An optional date argument, required for parsing DryCal files. Otherwise the date
        is parsed from ``fn``.

    Returns
    -------
    (data, metadata, fulldate) : tuple[list, dict, bool]
        Tuple containing the timesteps, metadata, and full date tag. Whether full date
        is returned depends on the file parser.

    """
    if parameters.calfile is not None:
        with open(parameters.calfile, "r") as infile:
            calib = json.load(infile)
    else:
        calib = {}
    if parameters.convert is not None:
        calib.update(parameters.convert)

    metadata = {}

    if parameters.filetype.startswith("drycal"):
        fulldate = False

        if "flow" not in calib:
            logger.info("Adding a default 'DryCal' -> 'flow' conversion")
            calib["flow"] = {"DryCal": {"calib": {"linear": {"slope": 1.0}}}}

        if parameters.filetype.endswith(".rtf") or fn.endswith("rtf"):
            ts, meta = drycal.rtf(fn, encoding, timezone, calib)
        elif parameters.filetype.endswith(".csv") or fn.endswith("csv"):
            ts, meta = drycal.sep(fn, ",", encoding, timezone, calib)
        elif parameters.filetype.endswith(".txt") or fn.endswith("txt"):
            ts, meta = drycal.sep(fn, "\t", encoding, timezone, calib)

    metadata.update(meta)

    return ts, metadata, fulldate