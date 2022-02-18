"""Provides a Configuration class and functionality."""

import os.path
import yaml
import experiments.command_line as command_line


class Benchmark:
    """
    Encapsulates meta-data about a single-object tracking benchmark.

    A benchmark is a collection of datasets and evaluation protocols. An example is OTB. It has two
    datasets: TB-50 and TB-100, and two evaluation protocols: overlap success and precision.

    Attributes:
        name (str): This is the name of the benchmark. Examples include OTB, UAV, and VOT.
        path (str): This is the root path to the benchmark datasets. The flatfoot tool will find the
            benchmark's datasets in this directory.
        versions (list): These are the datasets or versions available for the benchmark. Examples
            ``tb50`` and ``tb100`` for the OTB benchmark, and ``2019`` for the VOT benchmark.
    """

    def __init__(self, name: str, path: str, versions) -> None:
        self.name = name
        self.path = path
        if isinstance(versions, list):
            self.versions = versions
        else:
            self.versions = [versions]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name


class Tracker:
    def __init__(self, class_name: str, module_path: str) -> None:
        self.class_name = class_name
        self.path = os.path.dirname(module_path)
        self.module = os.path.splitext(os.path.basename(module_path))[0]

    @property
    def full_path(self) -> str:
        return os.path.join(self.path, f"{self.module}.py")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.class_name == other
        return self.class_name == other.class_name


class Configuration:
    def __init__(self) -> None:
        self.trackers = []
        self.benchmarks = []
        self.results_dir = os.path.abspath("results")
        self.report_dir = os.path.abspath("reports")
        self.primary_tracker = None

    def tracker(self, name: str) -> Tracker:
        return self.trackers[self.trackers.index(name)]

    def benchmark(self, name: str) -> Benchmark:
        return self.benchmarks[self.benchmarks.index(name)]


def load_configuration(user_file: str) -> Configuration:
    """
    Search for and load the flatfoot configuration file.

    If an error occurs during loading, the function prints an error message to the terminal, then
    exits.

    Args:
        user_file (str): Load this configuration file as requested by the user. If this is ``None``,
            flatfoot searches for the default options. If this file is not ``None`` and does not
            exist, flatfoot raises an exception.

    Returns:
        Configuration: This function returns the configuration read from the specified
        ``user_file``, or one of the default files.
    """
    try:
        return _try_load_configuration(user_file)
    except FileNotFoundError as error:
        command_line.print_error_and_exit(error.strerror, "-", error.filename)
    except KeyError as error:
        command_line.print_error_and_exit(
            "The required key", error.args[0], "is missing from the configuration."
        )


def _try_load_configuration(user_file: str) -> Configuration:
    if not user_file:
        user_file = _find_default_configuration_file()
    with open(user_file, "r") as configuration_file:
        configuration_data = yaml.safe_load(configuration_file)
    config = Configuration()
    config.trackers = _parse_trackers_from_yaml(configuration_data["trackers"])
    config.benchmarks = _parse_benchmarks_from_yaml(configuration_data["benchmarks"])
    if "results_dir" in configuration_data:
        config.results_dir = _sanitize_path(configuration_data["results_dir"])
    if "report_dir" in configuration_data:
        config.report_dir = _sanitize_path(configuration_data["report_dir"])
    if "primary_tracker" in configuration_data:
        config.primary_tracker = configuration_data["primary_tracker"]
    return config


def _sanitize_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def _find_default_configuration_file() -> str:
    if os.path.isfile(".flatfoot"):
        return ".flatfoot"
    if os.path.isfile(".flatfoot.yml"):
        return ".flatfoot.yml"
    if os.path.isfile(".flatfoot.yaml"):
        return ".flatfoot.yaml"
    raise FileNotFoundError("I could not find a default flatfoot configuration file.")


def _parse_trackers_from_yaml(yaml_data: list) -> list:
    trackers = []
    for yaml_datum in yaml_data:
        trackers.append(
            Tracker(yaml_datum["class"], os.path.expanduser(yaml_datum["path"]))
        )
    return trackers


def _parse_benchmarks_from_yaml(yaml_data: list) -> list:
    benchmarks = []
    for yaml_datum in yaml_data:
        benchmarks.append(
            Benchmark(
                yaml_datum["name"],
                os.path.expanduser(yaml_datum["path"]),
                yaml_datum["versions"],
            )
        )
    return benchmarks


def list_trackers(trackers: list) -> None:
    """
    List the trackers in the terminal.

    Args:
        trackers (list): Print this list of trackers.
    """
    for tracker in trackers:
        print(tracker.class_name, "  ", os.path.join(tracker.full_path))


def list_benchmarks(benchmarks: list) -> None:
    """
    List the benchmarks in the terminal.

    Args:
        benchmarks (list): Print this list of benchmarks.
    """
    for benchmark in benchmarks:
        print(benchmark.name, "  ", benchmark.path, "  ", benchmark.versions)
