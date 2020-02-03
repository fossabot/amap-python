[![Python Version](https://img.shields.io/pypi/pyversions/amap.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/amap.svg)](https://pypi.org/project/camap)
[![Wheel](https://img.shields.io/pypi/wheel/amap.svg)](https://pypi.org/project/amap)
[![Development Status](https://img.shields.io/pypi/status/amap.svg)](https://github.com/SainsburyWellcomeCentre/amap-python)
[![Travis](https://img.shields.io/travis/com/SainsburyWellcomeCentre/amap-python?label=Travis%20CI)](
    https://travis-ci.com/SainsburyWellcomeCentre/amap-python)
[![Coverage Status](https://coveralls.io/repos/github/SainsburyWellcomeCentre/amap-python/badge.svg?branch=master)](https://coveralls.io/github/SainsburyWellcomeCentre/amap-python?branch=master)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=SainsburyWellcomeCentre/amap-python)](https://dependabot.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![DOI](https://zenodo.org/badge/225904061.svg)](https://zenodo.org/badge/latestdoi/225904061)


# amap-python
Automated mouse atlas propagation


## About
amap is python software for registration of brain templates to sample whole-brain
microscopy datasets, and subsequent atlas-based segmentation by
[Adam Tyson](https://github.com/adamltyson), 
[Charly Rousseau](https://github.com/crousseau) & 
[Christian Niedworok](https://github.com/cniedwor) 
from the [Margrie Lab at the Sainsbury Wellcome Centre](https://www.sainsburywellcome.org/web/groups/margrie-lab).


This is a Python port of 
[aMAP](https://github.com/SainsburyWellcomeCentre/aMAP/wiki) (originally 
written in Java), which has been 
[validated against human segmentation](https://www.nature.com/articles/ncomms11879).


## Installation
```bash
pip install amap
```

## Usage
**N.B. Usage is currently fairly limited, only the following use cases are supported:** 
* Data must be in a series of 2D coronal sections
* Data must be registered to the 2017 Allen Institute reference adult mouse

amap was designed with generality in mind, so if anyone has different uses 
(e.g. requires a different atlas, or the data is in a different format), please get in touch 
by [email](mailto:adam.tyson@ucl.ac.uk?subject=amap) or by 
[raising an issue](https://github.com/SainsburyWellcomeCentre/amap-python/issues/new/choose).

### Basic usage
```bash
amap /path/to/raw/data /path/to/output/directory -x 2 -y 2 -z 5
```

### Arguments
#### Mandatory
* Path to the directory of the images. 
Can also be a text file pointing to the files.  
 * Output directory for all intermediate and final 
results

**Either**
* `-x` or `--x-pixel-mm` Pixel spacing of the data in the first dimension, 
specified in mm.
* `-y` or `--y-pixel-mm` Pixel spacing of the data in the second dimension, 
specified in mm.
* `-z` or `--z-pixel-mm` Pixel spacing of the data in the third dimension, 
specified in mm.

**Or**
* `--metadata` Metadata file containing pixel sizes (any format supported 
by [micrometa](https://github.com/adamltyson/micrometa) can be used).
  If both pixel sizes and metadata are provided, the command line arguments 
  will take priority.

#### Additional options
* `-d` or `--downsample` Paths to N additional channels to downsample to the 
same coordinate space.

Full command-line arguments are available with `amap -h`, but please 
[get in touch](mailto:adam.tyson@ucl.ac.uk?subject=amap) if you have any questions.


### Citing amap.

If you find amap useful, and use it in your research, please cite the [original Nature Communications paper](https://www.nature.com/articles/ncomms11879) along with this repository:

> Adam L. Tyson, Charly V. Rousseau, Christian J. Niedworok and Troy W. Margrie (2019). amap: automatic atlas propagation. [doi:10.5281/zenodo.3582162](https://zenodo.org/record/3582162)


### Visualisation
amap has a built in visualisation function (built using [napari](https://github.com/napari/napari)).

#### Usage
```bash
amap_vis /path/to/amap/output/directory
```

#### Mandatory
* Path to amap output directory


#### Additional options
* `-r` or `--raw`. Rather than viewing the downsampled data, view the raw data 
at full resolution. This will stream image planes as required, and so may be 
slow.
* `-c` or `--raw-channels` Paths to N additional channels to view. 
Will only work if using the raw image viewer.

N.B. If you have a high-resolution monitor, the scaling of the viewer may not work,
this is a [known napari issue](https://github.com/napari/napari/issues/367).

![amap_viewer](resources/amap_vis.gif)
