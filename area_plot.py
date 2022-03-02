"""Plots comparing bounding box dimensions."""

import os.path
import matplotlib.pyplot
import numpy
import got10k.experiments


def area_diff_plot(results_dir: str, sequence: str, trackers: list) -> None:
    experiment = got10k.experiments.ExperimentOTB(
        os.path.expanduser("~/Videos/otb"), version="tb100", result_dir=results_dir,
    )
    baseline_boxes, experimental_boxes = load_tracking_boxes(experiment, sequence, trackers)
    dimension_diffs = experimental_boxes[:, 2:] - baseline_boxes[:, 2:]
    plot = PerFrameFigure(sequence, trackers)
    plot.add_plot(_calculate_iou_diffs(experiment, sequence, trackers), "Δ Overlap Success")
    plot.add_plot(dimension_diffs[:, 0], "Δ Bounding Box Width (pixels)")
    plot.add_plot(dimension_diffs[:, 1], "Δ Bounding Box Height (pixels)")
    plot.show()


def load_tracking_boxes(
    experiment: got10k.experiments.ExperimentOTB, sequence: str, trackers: list
) -> tuple:
    baseline_boxes = numpy.loadtxt(
        os.path.join(experiment.result_dir, trackers[0], f"{sequence}.txt"), delimiter=","
    )
    experimental_boxes = numpy.loadtxt(
        os.path.join(experiment.result_dir, trackers[1], f"{sequence}.txt"), delimiter=","
    )
    return baseline_boxes, experimental_boxes


def _calculate_iou_diffs(
    experiment: got10k.experiments.ExperimentOTB, sequence: str, trackers: list
) -> numpy.ndarray:
    _, ground_truth = experiment.dataset[sequence]
    baseline_ious, _ = experiment._calc_metrics(
        numpy.loadtxt(
            os.path.join(experiment.result_dir, trackers[0], f"{sequence}.txt"), delimiter=",",
        ),
        ground_truth,
    )
    experimental_ious, _ = experiment._calc_metrics(
        numpy.loadtxt(
            os.path.join(experiment.result_dir, trackers[1], f"{sequence}.txt"), delimiter=",",
        ),
        ground_truth,
    )
    return experimental_ious - baseline_ious


class PerFrameFigure:
    def __init__(self, sequence: str, trackers: list = None):
        # self.figure = matplotlib.pyplot.figure()
        self.figure, self.axes = matplotlib.pyplot.subplots(nrows=3, ncols=1, sharex=True)
        title = f"{sequence} Sequence"
        if trackers:
            title = title + f" — {trackers[1]} - {trackers[0]}"
        self.figure.suptitle(title)
        # self.axes = []
        self.next_subplot = 0

    def add_plot(self, data: numpy.ndarray, y_label: str):
        self.axes[self.next_subplot].stem(
            range(1, data.shape[0] + 1),
            data,
            # label=f"{trackers[1]} - {trackers[0]}",
        )
        self.axes[self.next_subplot].set_ylabel(y_label)
        # self.axes[0].set_title(f"Δ Bounding Box Width per Frame — {sequence} Sequence")
        self.axes[self.next_subplot].grid(visible=True)
        # self.axes[-1].legend()
        self.axes[self.next_subplot].set_xticks(ticks=range(0, data.shape[0] + 1, 10))
        self.axes[self.next_subplot].set_xmargin(0.01)
        self.next_subplot += 1

    def show(self):
        self.axes[-1].set_xlabel("Frame")
        matplotlib.pyplot.show()
