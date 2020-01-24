import pytest
import random
import os

from pathlib import Path
from random import shuffle

import amap.tools.general as tools
import amap.tools.system as system

data_dir = Path("tests", "data")
cubes_dir = data_dir / "cubes"
jabberwocky = data_dir / "general" / "jabberwocky.txt"
jabberwocky_sorted = data_dir / "general" / "jabberwocky_sorted.txt"

cubes = [
    "pCellz222y2805x9962Ch1.tif",
    "pCellz222y2805x9962Ch2.tif",
    "pCellz258y3892x10559Ch1.tif",
    "pCellz258y3892x10559Ch2.tif",
    "pCellz413y2308x9391Ch1.tif",
    "pCellz413y2308x9391Ch2.tif",
    "pCellz416y2503x5997Ch1.tif",
    "pCellz416y2503x5997Ch2.tif",
    "pCellz418y5457x9489Ch1.tif",
    "pCellz418y5457x9489Ch2.tif",
    "pCellz433y4425x7552Ch1.tif",
    "pCellz433y4425x7552Ch2.tif",
]


sorted_cubes_dir = [os.path.join(str(cubes_dir), cube) for cube in cubes]


def write_n_random_files(n, dir, min_size=32, max_size=2048):
    sizes = random.sample(range(min_size, max_size), n)
    for size in sizes:
        with open(os.path.join(dir, str(size)), "wb") as fout:
            fout.write(os.urandom(size))


def test_check_path_in_dir():
    assert system.check_path_in_dir(jabberwocky, data_dir / "general")


def write_file_single_size(directory, file_size):
    with open(os.path.join(directory, str(file_size)), "wb") as fout:
        fout.write(os.urandom(file_size))


def check_get_num_processes():
    assert len(os.sched_getaffinity(0)) == system.get_num_processes()


def check_max_processes():
    max_proc = 5
    correct_n = min(len(os.sched_getaffinity(0)), max_proc)
    assert correct_n == system.get_num_processes(n_max_processes=max_proc)
