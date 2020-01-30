import os
import logging
import tempfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
from fancylog import fancylog
from pathlib import Path
from shutil import copyfile

from micrometa.micrometa import SUPPORTED_METADATA_TYPES
from imlib.general.system import ensure_directory_exists
from imlib.general.numerical import check_positive_int, check_positive_float
from imlib.image.metadata import define_pixel_sizes
from imlib.general.config import get_config_obj

from amap.download.cli import atlas_parser, download_directory_parser
from amap.main import main as register
from amap.tools import source_files
from amap.download import atlas as atlas_download
from amap.download.download import amend_cfg
import amap as program_for_log


temp_dir = tempfile.TemporaryDirectory()
temp_dir_path = temp_dir.name


def register_cli_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser = cli_parse(parser)
    parser = visualisation_parser(parser)
    parser = registration_parse(parser)
    parser = pixel_parser(parser)
    parser = geometry_parser(parser)
    parser = misc_parse(parser)
    parser = atlas_parser(parser)
    parser = download_directory_parser(parser)

    return parser


def cli_parse(parser):
    cli_parser = parser.add_argument_group("amap registration options")

    cli_parser.add_argument(
        dest="image_paths",
        type=str,
        help="Path to the directory of the image files. Can also be a text"
        "file pointing to the files.",
    )

    cli_parser.add_argument(
        dest="registration_output_folder",
        type=str,
        help="Directory to save the cubes into",
    )

    cli_parser.add_argument(
        "-d",
        "--downsample",
        dest="downsample_images",
        type=str,
        nargs="+",
        help="Paths to N additional channels to downsample to the same "
        "coordinate space. ",
    )
    return parser


def misc_parse(parser):
    misc_parser = parser.add_argument_group("Misc options")
    misc_parser.add_argument(
        "--n-free-cpus",
        dest="n_free_cpus",
        type=check_positive_int,
        default=4,
        help="The number of CPU cores on the machine to leave "
        "unused by the program to spare resources.",
    )

    misc_parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Debug mode. Will increase verbosity of logging and save all "
        "intermediate files for diagnosis of software issues.",
    )
    misc_parser.add_argument(
        "--metadata",
        dest="metadata",
        type=Path,
        help="Path to the metadata file. Supported formats are '{}'.".format(
            SUPPORTED_METADATA_TYPES
        ),
    )
    return parser


def pixel_parser(parser):
    pixel_opt_parser = parser.add_argument_group(
        "Options to define pixel sizes of raw data"
    )
    pixel_opt_parser.add_argument(
        "-x",
        "--x-pixel-um",
        dest="x_pixel_um",
        type=check_positive_float,
        help="Pixel spacing of the data in the first "
        "dimension, specified in um.",
    )
    pixel_opt_parser.add_argument(
        "-y",
        "--y-pixel-um",
        dest="y_pixel_um",
        type=check_positive_float,
        help="Pixel spacing of the data in the second "
        "dimension, specified in um.",
    )
    pixel_opt_parser.add_argument(
        "-z",
        "--z-pixel-um",
        dest="z_pixel_um",
        type=check_positive_float,
        help="Pixel spacing of the data in the third "
        "dimension, specified in um.",
    )
    return parser


def geometry_parser(parser):
    geometry_opt_parser = parser.add_argument_group(
        "Options to define size/shape/orientation of data"
    )
    geometry_opt_parser.add_argument(
        "--orientation",
        type=str,
        choices=("coronal", "sagittal", "horizontal"),
        default="coronal",
        help="The orientation of the sample brain. "
        "This is used to transpose the atlas"
        "into the same orientation as the brain.",
    )

    # Warning: atlas reference
    geometry_opt_parser.add_argument(
        "--flip-x",
        dest="flip_x",
        action="store_true",
        help="If the supplied data does not match the NifTI standard "
        "orientation (origin is the most ventral, posterior, left voxel),"
        "then the atlas will be flipped to match the input data",
    )
    geometry_opt_parser.add_argument(
        "--flip-y",
        dest="flip_y",
        action="store_true",
        help="If the supplied data does not match the NifTI standard "
        "orientation (origin is the most ventral, posterior, left voxel),"
        "then the atlas will be flipped to match the input data",
    )
    geometry_opt_parser.add_argument(
        "--flip-z",
        dest="flip_z",
        action="store_true",
        help="If the supplied data does not match the NifTI standard "
        "orientation (origin is the most ventral, posterior, left voxel),"
        "then the atlas will be flipped to match the input data",
    )

    return parser


def visualisation_parser(parser):
    vis_parser = parser.add_argument_group(
        "Options relating to registration visualisation"
    )

    vis_parser.add_argument(
        "--no-boundaries",
        dest="no_boundaries",
        action="store_true",
        help="Do not precompute the outline images (if you don't want to"
        " use amap_vis",
    )
    return parser


def registration_parse(parser):
    registration_opt_parser = parser.add_argument_group("Registration options")
    registration_opt_parser.add_argument(
        "--registration-config",
        dest="registration_config",
        type=str,
        help="To supply your own, custom registration configuration file.",
    )
    registration_opt_parser.add_argument(
        "--sort-input-file",
        dest="sort_input_file",
        action="store_true",
        help="If set to true, the input text file will be sorted using "
        "natural sorting. This means that the file paths will be "
        "sorted as would be expected by a human and "
        "not purely alphabetically",
    )

    registration_opt_parser.add_argument(
        "--no-save-downsampled",
        dest="no_save_downsampled",
        action="store_true",
        help="Dont save the downsampled brain before filtering.",
    )

    registration_opt_parser.add_argument(
        "--affine-n-steps",
        dest="affine_n_steps",
        type=check_positive_int,
        default=6,
    )
    registration_opt_parser.add_argument(
        "--affine-use-n-steps",
        dest="affine_use_n_steps",
        type=check_positive_int,
        default=5,
    )
    registration_opt_parser.add_argument(
        "--freeform-n-steps",
        dest="freeform_n_steps",
        type=check_positive_int,
        default=6,
    )
    registration_opt_parser.add_argument(
        "--freeform-use-n-steps",
        dest="freeform_use_n_steps",
        type=check_positive_int,
        default=4,
    )
    registration_opt_parser.add_argument(
        "--bending-energy-weight",
        dest="bending_energy_weight",
        type=check_positive_float,
        default=0.95,
    )
    registration_opt_parser.add_argument(
        "--grid-spacing-x", dest="grid_spacing_x", type=int, default=-10
    )
    registration_opt_parser.add_argument(
        "--smoothing-sigma-reference",
        dest="smoothing_sigma_reference",
        type=float,
        default=-1.0,
    )
    registration_opt_parser.add_argument(
        "--smoothing-sigma-floating",
        dest="smoothing_sigma_floating",
        type=float,
        default=-1.0,
    )
    registration_opt_parser.add_argument(
        "--histogram-n-bins-floating",
        dest="histogram_n_bins_floating",
        type=check_positive_int,
        default=128,
    )
    registration_opt_parser.add_argument(
        "--histogram-n-bins-reference",
        dest="histogram_n_bins_reference",
        type=check_positive_int,
        default=128,
    )
    return parser


def check_atlas_install():
    """
    Checks whether the atlas directory exists, and whether it's empty or not.
    :return: Whether the directory exists, and whether the files also exist
    """
    dir_exists = False
    files_exist = False
    cfg_file_path = source_files.source_custom_config()
    if os.path.exists(cfg_file_path):
        config_obj = get_config_obj(cfg_file_path)
        atlas_conf = config_obj["atlas"]
        atlas_directory = atlas_conf["base_folder"]
        if os.path.exists(atlas_directory):
            dir_exists = True
            if not os.listdir(atlas_directory) == []:
                files_exist = True

    return dir_exists, files_exist


def copy_registration_config(registration_config, output_directory):
    destination = Path(output_directory, "config.conf")
    copyfile(registration_config, destination)


def prep_registration(args):
    logging.info("Checking whether the atlas exists")
    _, atlas_files_exist = check_atlas_install()
    if not atlas_files_exist:
        logging.warning("Atlas does not exist, downloading.")
        if args.download_path is None:
            args.download_path = os.path.join(temp_dir_path, "atlas.tar.gz")
        atlas_download.main(args.atlas, args.install_path, args.download_path)
        amend_cfg(
            new_atlas_folder=args.install_path, atlas=args.atlas,
        )
    if args.registration_config is None:
        args.registration_config = source_files.source_custom_config()

    logging.debug("Making registration directory")
    ensure_directory_exists(args.registration_output_folder)

    logging.debug("Copying registration config to output directory")
    copy_registration_config(
        args.registration_config, args.registration_output_folder
    )

    additional_images_downsample = {}
    if args.downsample_images:
        for idx, images in enumerate(args.downsample_images):
            name = Path(images).name
            additional_images_downsample[name] = images

    return args, additional_images_downsample


def make_paths_absolute(args):
    args.image_paths = os.path.abspath(args.image_paths)
    args.registration_output_folder = os.path.abspath(
        args.registration_output_folder
    )
    args.registration_config = os.path.abspath(args.registration_config)
    return args


def run():
    start_time = datetime.now()
    args = register_cli_parser().parse_args()
    args = define_pixel_sizes(args)

    args, additional_images_downsample = prep_registration(args)
    args = make_paths_absolute(args)

    fancylog.start_logging(
        args.registration_output_folder,
        program_for_log,
        variables=[args],
        verbose=args.debug,
        log_header="AMAP LOG",
        multiprocessing_aware=False,
    )

    logging.info("Starting registration")
    register(
        args.registration_config,
        args.image_paths,
        args.registration_output_folder,
        x_pixel_um=args.x_pixel_um,
        y_pixel_um=args.y_pixel_um,
        z_pixel_um=args.z_pixel_um,
        orientation=args.orientation,
        flip_x=args.flip_x,
        flip_y=args.flip_y,
        flip_z=args.flip_z,
        affine_n_steps=args.affine_n_steps,
        affine_use_n_steps=args.affine_use_n_steps,
        freeform_n_steps=args.freeform_n_steps,
        freeform_use_n_steps=args.freeform_use_n_steps,
        bending_energy_weight=args.bending_energy_weight,
        grid_spacing_x=args.grid_spacing_x,
        smoothing_sigma_reference=args.smoothing_sigma_reference,
        smoothing_sigma_floating=args.smoothing_sigma_floating,
        histogram_n_bins_floating=args.histogram_n_bins_floating,
        histogram_n_bins_reference=args.histogram_n_bins_reference,
        sort_input_file=args.sort_input_file,
        n_free_cpus=args.n_free_cpus,
        save_downsampled=not (args.no_save_downsampled),
        boundaries=not (args.no_boundaries),
        additional_images_downsample=additional_images_downsample,
        debug=args.debug,
    )

    logging.info("Finished. Total time taken: %s", datetime.now() - start_time)


def gui():
    from gooey import Gooey

    @Gooey(
        program_name="amap",
        default_size=(1000, 1000),
        required_cols=1,
        optional_cols=3,
    )
    def run_gui():
        run()

    run_gui()


def main():
    run()


if __name__ == "__main__":
    run()
