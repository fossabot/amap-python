import os

from imlib.general.system import ensure_directory_exists
from amap.download.download import download

default_atlas_name = "brain.nii"

# allen_2017 (default) and allen_2017_10um are the same
atlas_urls = {
    "allen_2017_10um": "https://gin.g-node.org/cellfinder/atlas/raw/master/allen_2017_10um.tar.gz",
    "allen_2017_100um": "https://gin.g-node.org/cellfinder/atlas/raw/master/allen_2017_100um.tar.gz",
}

download_requirements_gb = {
    "allen_2017_10um": 1.8,
    "allen_2017_100um": 0.003,
}

extract_requirements_gb = {
    "allen_2017_10um": 11.5,
    "allen_2017_100um": 0.015,
}


def main(atlas, atlas_dir, download_path):
    if not os.path.exists(os.path.join(atlas_dir, atlas, default_atlas_name)):
        ensure_directory_exists(atlas_dir)

        download(
            download_path,
            atlas_urls[atlas],
            atlas,
            install_path=atlas_dir,
            download_requires=download_requirements_gb[atlas],
            extract_requires=extract_requirements_gb[atlas],
        )

    else:
        print(
            f"Atlas already exists at " f"{atlas_dir}." f" Skipping download"
        )
