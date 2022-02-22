"""Generate a plot of mean overlap success for each sequence in a dataset."""

import json


def generate_sequence_plot(performance_file: str) -> None:
    data = _load_performance_data(performance_file)
    return data


def _load_performance_data(performance_file_path: str) -> dict:
    with open(performance_file_path, "r") as performance_file:
        data = json.load(performance_file)
    if _is_vot_performance_data(data):
        raise RuntimeError("VOT performance data does not contain per-sequence data.")
    per_sequence_data = {}
    for tracker, tracker_data in data.items():
        per_sequence_data[tracker] = {
            sequence: sequence_data["success_score"]
            for sequence, sequence_data in tracker_data["seq_wise"].items()
        }
    return per_sequence_data


def _is_vot_performance_data(data: dict) -> bool:
    for tracker, tracker_data in data.items():
        if "accuracy" in tracker_data:
            return True
    return False
