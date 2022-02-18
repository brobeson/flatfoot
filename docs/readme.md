# Tracker Configuration

Tracker reads a YAML configuration file to learn where tracking algorithms and
datasets are on your system. By default, it looks for *.tracker*,
*.tracker.yaml*, and *.tracker.yml*, in that order. It uses the first file that
it finds. You can specify a particular configuration file on the command line.

## Configuration Options

The tracker configuration requires two root items: `trackers` and `benchmarks`.

Table 1 — Optional Configuration Settings

| Setting | Type | Default | Description |
|:---|:---|:---|:---|
| `results_dir` | string | results | The path for reading and writing tracking experiment results. |
| `report_dir` | string | reports | The path for writing tracking experiment reports. |

### trackers

The `trackers` option holds a list of trackers. Each tracker is a YAML object
with the properties defined in the table below. Conceptually, each tracker is a
Python module and class. This is how tracker knows how to import and instantiate
your tracker.

| Property | Type | Description |
|:---|:---|:---|
| `class` | string | The name of the tracker class within your tracker's Python module. |
| `module_path` | string | The path to your tracker's main module on your system. Tracker expands `~` automatically. Tracker appends the module's directory to Python's `sys.path` |

### benchmarks

The `benchmarks` object holds a list of tracking benchmark datasets. This
information is at a fairly high level. For example, you would define a VOT
benchmark, not a VOT 2021 benchmark. Tracker will locate the specific dataset
from the benchmark for you.

| Property | Type | Description |
|:---|:---|:---|
| `name` | string | The name of the benchmark. |
| `path` | string | The path to the benchmark on your system. |

## Example Configuration

```yaml
trackers:
  - class: Tmft
    path: ~/research/tmft/tmft.py
benchmarks:
  - name: OTB
    path: ~/Videos/otb
  - name: VOT
    path: ~/Videos/vot
  - name: UAV
    path: ~/Videos/uav
report_dir: ~/Documents/phd/dissertation/plots
```
