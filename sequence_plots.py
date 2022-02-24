"""Generate a plot of mean overlap success for each sequence in a dataset."""

import json
import statistics
import os.path
import matplotlib.pyplot
import numpy
import got10k.experiments


def tracker_diff_plot(performance_file: str, trackers: list = None) -> None:
    data = _load_performance_data(performance_file, trackers)
    _plot_stems(data, trackers)


def sequence_diff_plot(results_dir: str, sequence: str, trackers: list) -> None:
    experiment = got10k.experiments.ExperimentOTB(
        os.path.expanduser("~/Videos/otb"),
        version="tb100",
        result_dir=results_dir,  # os.path.expanduser("~/repositories/tmft/results"),
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


def _plot_stems(data: dict, trackers: list) -> None:
    matplotlib.pyplot.cla()
    matplotlib.pyplot.xlabel("Sequence")
    matplotlib.pyplot.xticks(rotation=-90)
    matplotlib.pyplot.ylabel("Δ Overlap Success")
    matplotlib.pyplot.title(f"Δ Overlap Success per Sequence")
    matplotlib.pyplot.grid(axis="x")
    baseline_tracker = trackers[0]
    experiment_tracker = trackers[1]
    x_values = list(data[baseline_tracker].keys())
    deltas = [
        data[experiment_tracker][sequence] - data[baseline_tracker][sequence]
        for sequence in x_values
    ]
    matplotlib.pyplot.stem(x_values, deltas, label=f"{trackers[1]} - {trackers[0]}")
    mean = statistics.mean(deltas)
    matplotlib.pyplot.hlines(
        mean, x_values[0], x_values[-1], label=f"Mean Δ = {mean:.3f}", color="orange"
    )
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
