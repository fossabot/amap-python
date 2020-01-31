"""
source_files
===============

Return location of specific files specific to amap

"""


from pkg_resources import resource_filename
from amap.config.atlas import Atlas


def source_config():
    return resource_filename("amap", "amap.conf")


def source_custom_config():
    return resource_filename("amap", "amap.conf.custom")


def get_niftyreg_binaries():
    return resource_filename("amap", "bin/nifty_reg")


def get_structures_path(config=None):
    if config is None:
        config = source_custom_config()
    atlas = Atlas(config)
    return atlas.get_structures_path()
