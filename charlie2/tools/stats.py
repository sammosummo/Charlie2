"""Defines functions for calculating various summary statistics.


"""
from logging import getLogger
from typing import List

logger = getLogger(__name__)


def basic_summary(
    trials: List[dict], prefix: str = "", adjust: bool = False, no_practice: bool = True
) -> dict:
    """Returns an basic set of summary statistics.

    Args:
        trials (:obj:`list` of :obj:`dict` objects): List of trials to analyse. Each
            trial is a dictionary.
        prefix (:obj:`str`, optional): Prefix to prepend to statistic names. If empty
            (default), no prefix is prepended.
        adjust (:obj:`bool`, optional): Calculated "adjusted" time taken if not all
            trials were completed before a timeout event. Defaults to `False`.
        no_practice (:obj:`bool`, optional): Include practice trials in summary. Default
            is `False`. I don't see any reason to ever change this.

    Returns:
        dict: dictionary of results.

    """
    logger.debug("called basic_summary()")

    if len(trials) == 0:
        return {}

    # filter out practice trials
    if no_practice is True:
        trials_ = [t for t in trials if t["practice"] is False]
    else:
        trials_ = trials

    # check all trials are either "completed" or "skipped"
    completed_trials = [t for t in trials_ if t["status"] == "completed"]
    skipped_trials = [t for t in trials_ if t["status"] == "skipped"]
    n = len(completed_trials) + len(skipped_trials)
    if n != len(trials_):
        logger.warning("some trials have a status other than 'completed' or 'skipped'")

    # create dictionary
    dic = {
        "total_trials": len(trials_),
        "completed_trials": len(completed_trials),
        "skipped_trials": len(skipped_trials),
        "completed_or_skipped_trials": n,
        "correct_trials": len([t for t in trials_ if t["correct"] is True]),
    }

    # reaction time
    correct_trials = [t for t in trials_ if t["correct"] is True]
    if len(correct_trials) > 0:
        rts = [t["trial_time_elapsed_ms"] for t in correct_trials]
        dic["mean_rt_correct_ms"] = sum(rts) / len(rts)

    # times
    dic["started_timestamp"] = trials[0]["started_timestamp"]
    dic["finished_timestamp"] = trials[-1]["finished_timestamp"]
    dic["total_time_taken"] = dic["finished_timestamp"] - dic["started_timestamp"]

    if len(completed_trials) > 0:
        dic["block_duration_ms"] = completed_trials[-1]["block_time_elapsed_ms"]

    # adjusted block duration
    if adjust is True and len(correct_trials) > 0:
        extra_time = dic["mean_rt_correct_ms"] * len(skipped_trials)
        dic["block_duration_ms_adjusted"] = dic["block_duration_ms"] + extra_time

    # accuracy
    try:
        dic["accuracy"] = len(correct_trials) / len(trials_)
    except ZeroDivisionError:
        dic["accuracy"] = 0

        # format prefix
    if prefix != "":
        p = f"{prefix}_"
    else:
        p = ""

    # prepend prefix
    dic = {p + k: v for k, v in dic.items()}

    return dic
