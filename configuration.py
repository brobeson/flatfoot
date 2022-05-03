"""Provides a Configuration class and functionality."""

import os.path
import yaml


class Benchmark:
    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.name == other
        return self.name == other.name


class Tracker:
    def __init__(self, class_name: str, module_path: str) -> None:
        self.class_name = class_name
        self.path = os.path.dirname(module_path)
        self.module = os.path.splitext(os.path.basename(module_path))[0]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.class_name == other
        return self.class_name == other.class_name


class Configuration:
    def __init__(self) -> None:
        self.trackers = []
        self.benchmarks = []

    def tracker(self, name: str) -> Tracker:
        return self.trackers[self.trackers.index(name)]

    def benchmark(self, name: str) -> Benchmark:
        return self.benchmarks[self.benchmarks.index(name)]


def load_configuration(user_file: str) -> Configuration:
    """
    Search for and load the flatfoot configuration file.

    Args:
        user_file (str): Load this configuration file as requested by the user. If this is ``None``,
            flatfoot searches for the default options. If this file is not ``None`` and does not
            exist, flatfoot raises an exception.

    Returns:
        Configuration: This function returns the configuration read from the specified
        ``user_file``, or one of the default files.

    Raises:
        FileNotFoundError: This function raises a :py:exception:`FileNotFoundError` if it cannot
            find a configuration file.
        KeyError: This function raises a :py:exception:`KeyError` if required keys are in the
            configuration file.
    """
    if not user_file:
        user_file = _find_default_configuration_file()
    with open(user_file, "r") as configuration_file:
        configuration_data = yaml.safe_load(configuration_file)
    config = Configuration()
    config.trackers = _parse_trackers_from_yaml(configuration_data["trackers"])
    config.benchmarks = _parse_benchmarks_from_yaml(configuration_data["benchmarks"])
    return config


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
            Benchmark(yaml_datum["name"], os.path.expanduser(yaml_datum["path"]))
        )
    return benchmarks
