"""Generate a plot of mean overlap success for each sequence in a dataset."""

import json
import matplotlib.pyplot


def generate_sequence_plot(performance_file: str, trackers: list = None) -> None:
    data = _load_performance_data(performance_file, trackers)
    # _plot_sequence_data(data)
    _plot_stems(data, trackers)


def _load_performance_data(performance_file_path: str, trackers: list = None) -> dict:
    with open(performance_file_path, "r") as performance_file:
        data = json.load(performance_file)
    if _is_vot_performance_data(data):
        raise RuntimeError("VOT performance data does not contain per-sequence data.")
    per_sequence_data = {}
    for tracker, tracker_data in data.items():
        if tracker in trackers:
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


def _plot_sequence_data(data: dict) -> None:
    matplotlib.pyplot.cla()
    matplotlib.pyplot.xlabel("Sequence")
    matplotlib.pyplot.ylabel("Mean Overlap Success")
    matplotlib.pyplot.title("Mean Overlap Success per Sequence")
    for tracker, tracker_data in data.items():
        _plot_one_tracker(tracker, tracker_data)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()


def _plot_stems(data: dict, trackers: list) -> None:
    matplotlib.pyplot.cla()
    matplotlib.pyplot.xlabel("Sequence")
    matplotlib.pyplot.xticks(rotation=-90)
    matplotlib.pyplot.ylabel("Delta Mean Overlap Success")
    matplotlib.pyplot.title(f"Delta Mean Overlap Success: {trackers[1]}-{trackers[0]}")
    matplotlib.pyplot.grid(axis="x")
    baseline_tracker = trackers[0]
    experiment_tracker = trackers[1]
    deltas = [
        data[experiment_tracker][sequence] - data[baseline_tracker][sequence]
        for sequence in data[baseline_tracker].keys()
    ]
    # matplotlib.pyplot.stem(range(0, len(deltas)), deltas)
    matplotlib.pyplot.stem(data[baseline_tracker].keys(), deltas)
    matplotlib.pyplot.show()


def _plot_one_tracker(tracker: str, data: dict) -> None:
    matplotlib.pyplot.plot(
        range(0, len(data)),
        data.values(),
        marker="o",
        label=tracker,
    )
