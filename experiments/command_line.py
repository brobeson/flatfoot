"""
This module provides convenient functionality for interacting with the terminal and the command
line.
"""

import argparse
import os.path
import sys


class PathSanitizer(argparse.Action):
    """
    Ensures path arguments are absolute and expands '~'.

    To use this, just pass it to `argparse.ArgumentParser.add_argument()
    <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument>`_
    as the ``action``.

    .. code-block:: python

        import experiments.command_line
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "file_path",
            action=experiments.command_line.PathSanitizer,
        )

    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def add_configuration_parameter(parser: argparse.ArgumentParser) -> argparse.Action:
    """
    Add the ``--configuration`` parameter to a command line parser.

    This allows the user to specify a specific configuration for the flatfoot application.

    Args:
        parser (argparse.ArgumentParser): Add the parameter to this parser.

    Returns:
        argparse.Action: This function returns the :py:class:`argparse.Action` that represents the
        command line parameter. The caller can tweak the action if necessary.
    """
    return parser.add_argument(
        "--configuration",
        help="Run flatfoot with this configuration. If you omit this argument, flatfoot looks for "
        ".flatfoot, .flatfoot.yml, and .flatfoot.yaml in the current working directory. It uses "
        "the first configuration file that it finds.",
        action=PathSanitizer,
    )


def add_dataset_dir_parameter(
    parser: argparse.ArgumentParser, default: str
) -> argparse.Action:
    """
    Add the ``--dataset-dir`` parameter to a command line parser.

    This allows the user to specify the location to find a benchmark's image and annotation files.

    Args:
        parser (argparse.ArgumentParser): Add the parameter to this parser.
        default (str): Use this as the default argument for the parameter. This function expands
            '~' and converts it to an absolute path before adding the option to the ``parser``.

    Returns:
        argparse.Action: This function returns the :py:class:`argparse.Action` that represents the
        command line parameter. The caller can tweak the action if necessary.
    """
    return parser.add_argument(
        "--dataset-dir",
        help="This is the path to a tracking benchmark dataset. It is specific to one benchmark, "
        "such as OTB-100 or VOT 2019. The layout of the directory content is specific to each "
        "benchmark",
        default=os.path.abspath(os.path.expanduser(default)),
        action=PathSanitizer,
    )


def add_results_dir_parameter(parser: argparse.ArgumentParser) -> argparse.Action:
    """
    Add the ``--results-dir`` parameter to a command line parser.

    This allows the user to specify the location to read or write tracking experiment results files.

    Args:
        parser (argparse.ArgumentParser): Add the ``--results-dir`` parameter to this parser.

    Returns:
        argparse.Action: This function returns the :py:class:`argparse.Action` that represents the
        command line parameter. The caller can tweak the action if necessary.
    """
    return parser.add_argument(
        "--results-dir",
        help="This is the path to the directory containing tracking results. Commands that "
        "generate tracking results write them to this directory in benchmark child directories. "
        "Commands that use tracking results read from this directory, from benchmark child "
        "directories.",
        default=os.path.abspath("./results"),
        action=PathSanitizer,
    )


def add_tracker_parameter(parser: argparse.ArgumentParser) -> argparse.Action:
    """
    Add the ``--tracker`` parameter to a command line parser.

    This allows the user to select a specific tracker from the flatfoot configuration.

    Args:
        parser (argparse.ArgumentParser): Add the parameter to this parser.

    Returns:
        argparse.Action: This function returns the :py:class:`argparse.Action` that represents the
        command line parameter. The caller can tweak the action if necessary.
    """
    return parser.add_argument(
        "--tracker",
        help="Use this tracker from the flatfoot configuration. This must be the 'class' property "
        "of the tracker in the configuration file.",
        default="MDNet",
    )


def add_list_trackers_parameter(parser: argparse.ArgumentParser) -> argparse.Action:
    """
    Add the ``--list-trackers`` parameter to a command line parser.

    This allows the user to list the trackers defined in the flatfoot configuration.

    Args:
        parser (argparse.ArgumentParser): Add the parameter to this parser.

    Returns:
        argparse.Action: This function returns the :py:class:`argparse.Action` that represents the
        command line parameter. The caller can tweak the action if necessary.
    """
    return parser.add_argument(
        "--list-trackers",
        help="List the trackers in the flatfoot configuration, then exit.",
        action="store_true",
    )


def add_list_benchmarks_parameter(parser: argparse.ArgumentParser) -> argparse.Action:
    """
    Add the ``--list-benchmarks`` parameter to a command line parser.

    This allows the user to list the benchmarks defined in the flatfoot configuration.

    Args:
        parser (argparse.ArgumentParser): Add the parameter to this parser.

    Returns:
        argparse.Action: This function returns the :py:class:`argparse.Action` that represents the
        command line parameter. The caller can tweak the action if necessary.
    """
    return parser.add_argument(
        "--list-benchmarks",
        help="List the benchmarks in the flatfoot configuration, then exit.",
        action="store_true",
    )


def print_information(*objects) -> None:
    """
    Print an information message to the terminal using blue text.

    Args:
        objects: The data to print as an information message.
    """
    _print_message("\033[94m", *objects)


def print_warning(*objects) -> None:
    """
    Print a warning message to the terminal using orange text.

    Args:
        objects: The data to print as a warning.
    """
    _print_message("\033[91m", *objects)


def print_error(*objects) -> None:
    """
    Print an error message to the terminal using red text.

    Args:
        objects: The data to print as a warning.
    """
    _print_message("\033[91m", *objects)


def print_error_and_exit(*objects) -> None:
    """
    Print an error message to the terminal using red text, then exit with non-zero status.

    Args:
        objects: The data to print as a warning.
    """
    print_error(*objects)
    sys.exit(1)


def _print_message(color: str, *objects) -> None:
    print(color, end="")
    print(*objects, end="")
    print("\033[0m")
