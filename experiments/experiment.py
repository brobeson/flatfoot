"""
Run a tracking experiment.

This module runs a complete tracking experiment for a common tracking benchmark. This modules does
not create reports; see :py:mod:`experiments.report` for information about generating reports
from the experiment results.

Running this Module as a Script
-------------------------------

You can run this module as a stand-alone script.

.. literalinclude:: generated/experiment_help.rst
    :language: text

Importing this Module
---------------------

You can also use this module as part of a larger application.

#. Import this module.
#. Call :py:func:`fill_command_line_parser()`.
#. Parse the command line arguments.
#. Run ``arguments.func(arguments)`` or :py:func:`main()`.

Here is an example of using this module as the sole command line parser::

    import experiments.experiment as experiment
    parser = experiment.fill_command_line_parser(argparse.ArgumentParser())
    arguments = parser.parse_args()
    arguments.func(arguments)

Here is an example of using this module as a subcommand in a larger application::

    import experiments.experiment as experiment
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    experiment.fill_command_line_parser(subparsers.add_parser("report"))
    arguments = parser.parse_args()
    arguments.func(arguments)

Reference
---------
"""

import argparse
import datetime
import importlib
import os
import sys
from typing import Union
import got10k.experiments
import got10k.trackers
import configuration
import experiments.command_line as command_line
import experiments.slack_reporter as slack_reporter

OTB_VERSIONS = ["tb50", "tb100"]
VOT_VERSIONS = ["2019"]
UAV_VERSIONS = ["uav123"]


def fill_command_line_parser(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """
    Create the command line parser for this module.

    This function supports filling in a subparser or a root parser. In both cases, this function
    overwrites certain parser attributes, such as the description.

    Args:
        parser (argparse.ArgumentParser): Fill out this argument parser. This can be a root parser
            or a subparser created with `add_subparsers()
            <https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers>`_.

    Returns:
        The parser, filled with parameters and attributes, ready for command line parsing.
    """
    parser.description = "Run tracking experiments for a single benchmark."
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser.set_defaults(func=main)
    command_line.add_configuration_parameter(parser)
    command_line.add_tracker_parameter(parser)
    command_line.add_list_trackers_parameter(parser)
    command_line.add_list_benchmarks_parameter(parser)
    # command_line.add_dataset_dir_parameter(parser, "~/Videos")
    # command_line.add_results_dir_parameter(parser)
    # parser.add_argument(
    #     "--slack-file",
    #     help="Send notifications to a Slack channel. This option specifies the path to a file with "
    #     "the Slack channel information. See the documentation for the experiments.slack_reporter "
    #     "module for details about the file contents.",
    #     action=command_line.PathSanitizer,
    # )
    # parser.add_argument(
    #     "benchmark",
    #     help="Use this benchmark for the tracking experiment. 'tb50' and 'tb100' are OTB "
    #     "benchmarks. '2019' is the VOT 2019 short-term benchmark. 'uav123' is the UAV123 "
    #     "benchmark.",
    #     choices=OTB_VERSIONS + VOT_VERSIONS + UAV_VERSIONS,
    # )
    return parser


def main(arguments: argparse.Namespace) -> None:
    """
    The main entry point for this module.

    Typically, you don't need to invoke this function; instead use ``arguments.func()`` after you
    parse the command line arguments. See :py:func:`fill_command_line_parser()` for examples. If
    you do need to call this function, do so *after* parsing the command line.

    Args:
        arguments (argparse.Namespace): The parsed command line arguments. The ``arguments`` must
            have these attributes: ``tracker_name``, ``slack_file``, ``benchmark``, ``dataset_dir``,
            and ``results_dir``.
    """
    config = _load_configuration(arguments.configuration)
    _list_trackers_and_benchmarks(
        arguments.list_trackers, arguments.list_benchmarks, config
    )
    tracker = _import_tracker(config, arguments.tracker)
    experiments = _make_experiments(config.benchmarks)
    for experiment in experiments:
        _run_tracker(experiments, arguments.tracker_name, arguments.slack_file)


def _load_configuration(user_file: str) -> configuration.Configuration:
    try:
        return configuration.load_configuration(user_file)
    except FileNotFoundError as error:
        command_line.print_error(error.strerror, "-", error.filename)
        sys.exit(1)
    except KeyError as error:
        command_line.print_error(
            "The required key", error.args[0], "is missing from the configuration."
        )
        sys.exit(1)


def _list_trackers_and_benchmarks(
    list_trackers: bool, list_benchmarks: bool, config: configuration.Configuration
) -> None:
    if list_trackers or list_benchmarks:
        if list_trackers:
            configuration.list_trackers(config.trackers)
        if list_benchmarks:
            configuration.list_benchmarks(config.benchmarks)
        sys.exit(0)


def _import_tracker(
    flatfoot_configuration: configuration.Configuration, requested_tracker: str
) -> None:
    # TODO Allow the user to specify custom tracker __init__() arguments.
    # TODO Allow the user to set the tracker's name.
    if not flatfoot_configuration.trackers:
        command_line.print_error(
            "There are no trackers defined in the flatfoot configuration."
        )
        sys.exit(1)
    if requested_tracker in flatfoot_configuration.trackers:
        tracker_to_import = flatfoot_configuration.tracker(requested_tracker)
    else:
        if len(flatfoot_configuration.trackers) > 1:
            command_line.print_error(
                "You did not specify a tracker, and there are multiple trackers to select."
            )
            sys.exit(1)
        else:
            tracker_to_import = flatfoot_configuration.trackers[0]
    sys.path.append(tracker_to_import.path)
    try:
        module = importlib.import_module(tracker_to_import.module)
        tracker = getattr(module, tracker_to_import.class_name)()
        return tracker
    except ModuleNotFoundError as error:
        command_line.print_error(error.msg)
        command_line.print_error(
            "Ensure Python can find your tracker's modules using sys.path:"
        )
        command_line.print_error(sys.path)
        sys.exit(1)


# class _ConsoleReporter:
#     """
#     An alternative to :py:class`experiments.slack_reporter.SlackReporter`. This reporter prints
#     messages to the console.
#     """

#     def send_message(self, message: str) -> None:  # pylint: disable=no-self-use
#         """
#         Print a message to the console.

#         Args:
#             message (str): This is not used in the method.
#         """
#         print(message)


# def _make_notifier(
#     configuration_file: str, source: str
# ) -> Union[_ConsoleReporter, slack_reporter.SlackReporter]:
#     """
#     Make an appropriate notifier object.

#     Args:
#         configuration_file (str | None): The path to the Slack configuration file.
#         source (str): The source to use for Slack reporting.

#     Returns:
#         slack_reporter.SlackReporter | ConsoleReporter: If the function can load the
#         ``configuration_file``, the function returns a :py:class:`slack_reporter.SlackReporter`
#         object. Otherwise, the function returns a :py:class:`ConsoleReporter` object.
#     """
#     if configuration_file is not None and os.path.isfile(configuration_file):
#         return slack_reporter.SlackReporter(
#             source, **slack_reporter.read_slack_configuration(configuration_file)
#         )
#     return _ConsoleReporter()


def _make_experiments(benchmarks: list) -> list:
    """
    Create the GOT-10k experiment to run.

    Args:
        experiment_configuration (argparse.Namespace): The experiment configuration. This most
            likely comes from command line arguments.

    Returns:
        The GOT-10k experiment to run.
    """
    # TODO Allow the user to specify which benchmark to use.
    # TODO Allow the user to specify which version of the benchmark to use.
    # TODO Allow the user to specify the results directory.
    # TODO Allow the user to specify experiment details, such as the VOT experiment type.
    experiments = []
    for benchmark in benchmarks:
        benchmark_name = benchmark.name.lower()
        if benchmark_name == "otb":
            for version in benchmark.versions:
                experiments.append(
                    got10k.experiments.ExperimentOTB(benchmark.path, version=version)
                )
        elif benchmark_name == "vot":
            for version in benchmark.versions:
                experiments.append(
                    got10k.experiments.ExperimentVOT(benchmark.path, version=version)
                )
        elif benchmark_name == "uav":
            for version in benchmark.versions:
                experiments.append(
                    got10k.experiments.ExperimentUAV123(benchmark.path, version=version)
                )
        else:
            command_line.print_error("Unknown benchmark:", benchmark.name)
            sys.exit(1)
    return experiments


def _run_tracker(experiment, tracker) -> None:
    """
    Run an experiment based on the GOT-10k toolkit.

    Args:
        experiment: The GOT-10k experiment object to run.
        tracker_name (str): The name of the tracker to run within the ``experiment``.
        slack_file (str | None): The Slack configuration file. If this is ``None``, console
            notifications are used.
    """
    # notifier = _make_notifier(slack_file, sys.platform)
    # notifier.send_message(
    #     f"Starting {tracker_name} {str(experiment.dataset.version)} experiment at "
    #     f"{datetime.datetime.today().isoformat(sep=' ', timespec='minutes')}"
    # )
    # try:
    experiment.run(tracker)
    # except Exception as error:  # pylint: disable=broad-except
    #     notifier.send_message(f"Error during experiment: '{str(error)}'")
    # else:
    #     notifier.send_message(
    #         "Experiment finished at "
    #         + datetime.datetime.today().isoformat(sep=" ", timespec="minutes")
    #     )


if __name__ == "__main__":
    PARSER = fill_command_line_parser(argparse.ArgumentParser())
    ARGUMENTS = PARSER.parse_args()
    ARGUMENTS.func(ARGUMENTS)
