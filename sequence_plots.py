"""Generate a plot of mean overlap success for each sequence in a dataset."""

import json
import os.path
import matplotlib.pyplot
import numpy
import got10k.experiments


def tracker_diff_plot(performance_file: str, trackers: list = None) -> None:
    data = _load_performance_data(performance_file, trackers)
    # _plot_sequence_data(data)
    _plot_stems(data, trackers)


def sequence_diff_plot(sequence: str, trackers: list) -> None:
    experiment = got10k.experiments.ExperimentOTB(
        os.path.expanduser("~/Videos/otb"),
        version="tb100",
        result_dir=os.path.expanduser("~/repositories/tmft/results"),
    )
    _, ground_truth = experiment.dataset[sequence]
    baseline_ious, _ = experiment._calc_metrics(
        numpy.loadtxt(
            os.path.join(experiment.result_dir, trackers[0], f"{sequence}.txt"),
            delimiter=",",
        ),
        ground_truth,
    )
    experimental_ious, _ = experiment._calc_metrics(
        numpy.loadtxt(
            os.path.join(experiment.result_dir, trackers[1], f"{sequence}.txt"),
            delimiter=",",
        ),
        ground_truth,
    )
    _plot_frame_stems(baseline_ious, experimental_ious, trackers)


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
    matplotlib.pyplot.stem(data[baseline_tracker].keys(), deltas)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()


def _plot_frame_stems(
    baseline: numpy.ndarray, experimental: numpy.ndarray, trackers
) -> None:
    matplotlib.pyplot.cla()
    matplotlib.pyplot.xlabel("Frame")
    matplotlib.pyplot.ylabel("Delta Mean Overlap Success")
    matplotlib.pyplot.title(f"Delta Mean Overlap Success: {trackers[1]}-{trackers[0]}")
    matplotlib.pyplot.grid(axis="x")
    matplotlib.pyplot.stem(range(len(baseline)), experimental - baseline)
    matplotlib.pyplot.xticks(ticks=range(0, len(baseline), 10), rotation=-90)
    matplotlib.pyplot.show()


def _plot_one_tracker(tracker: str, data: dict) -> None:
    matplotlib.pyplot.plot(
        range(0, len(data)),
        data.values(),
        marker="o",
        label=tracker,
    )
