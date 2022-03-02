"""Plots comparing bounding box dimensions."""

import os.path
import matplotlib.pyplot
import numpy
import got10k.experiments


def area_diff_plot(results_dir: str, sequence: str, trackers: list) -> None:
    baseline_boxes, experimental_boxes = load_tracking_boxes(results_dir, sequence, trackers)
    dimension_diffs = experimental_boxes[:, 2:] - baseline_boxes[:, 2:]
    _plot_dimensions(dimension_diffs, trackers, sequence)


def load_tracking_boxes(results_dir: str, sequence: str, trackers: list) -> tuple:
    experiment = got10k.experiments.ExperimentOTB(
        os.path.expanduser("~/Videos/otb"), version="tb100", result_dir=results_dir,
    )
    baseline_boxes = numpy.loadtxt(
        os.path.join(experiment.result_dir, trackers[0], f"{sequence}.txt"), delimiter=","
    )
    experimental_boxes = numpy.loadtxt(
        os.path.join(experiment.result_dir, trackers[1], f"{sequence}.txt"), delimiter=","
    )
    return baseline_boxes, experimental_boxes


def _plot_dimensions(dimension_diffs: numpy.ndarray, trackers, sequence: str) -> None:
    _, axes = matplotlib.pyplot.subplots(nrows=2, ncols=1, sharex=True)
    axes[0].stem(
        range(1, dimension_diffs.shape[0] + 1),
        dimension_diffs[:, 0],
        label=f"{trackers[1]} - {trackers[0]}",
    )
    axes[0].set_ylabel("Δ Bounding Box Width (pixels)")
    axes[0].set_title(f"Δ Bounding Box Width per Frame — {sequence} Sequence")
    axes[0].grid(visible=True)
    axes[0].legend()
    axes[1].stem(
        range(1, dimension_diffs.shape[0] + 1),
        dimension_diffs[:, 1],
        label=f"{trackers[1]} - {trackers[0]}",
    )
    axes[1].set_ylabel("Δ Bounding Box Height (pixels)")
    axes[1].set_title(f"Δ Bounding Box Height per Frame — {sequence} Sequence")
    axes[1].grid(visible=True)
    axes[1].legend()

    # These should affect both axes since they share the X dimension.
    axes[1].set_xmargin(0.01)
    axes[1].set_xlabel("Frame")
    axes[1].set_xticks(ticks=range(0, dimension_diffs.shape[0] + 1, 10))

    matplotlib.pyplot.show()
