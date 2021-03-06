"""
brain_registration
==================

The module to actually start the registration
"""

import os
import sys
import logging

from brainio import brainio


from imlib.general.system import (
    safe_execute_command,
    SafeExecuteCommandError,
)

from imlib.general.exceptions import RegistrationError, SegmentationError


class BrainRegistration(object):
    """
    A class to register brains using the nifty_reg set of binaries
    """

    def __init__(
        self,
        registration_config,
        paths,
        registration_params,
        n_processes=None,
    ):
        self.registration_config = registration_config
        self.paths = paths
        self.reg_params = registration_params
        if n_processes is not None:
            self.n_processes = n_processes
            self._prepare_openmp_thread_flag()
        else:
            self.n_processes = None

        self.dataset_img_path = paths.tmp__downsampled_filtered
        self.brain_of_atlas_img_path = paths.brain_filtered
        self.atlas_img_path = paths.annotations
        self.hemispheres_img_path = paths.hemispheres

    def sanitise_inputs(self):
        """
        Validates the inputs paths (dataset, atlas, brain of atlas) to
        check that they are the correct image type and that they exist.

        :return:
        :raises RegistrationError: If the conditions are not met
        """
        img_paths_var_names = (
            "dataset_img_path",
            "atlas_img_path",
            "brain_of_atlas_img_path",
        )
        for img_path_var_name in img_paths_var_names:
            img_path = getattr(self, img_path_var_name)
            if not os.path.exists(img_path):
                sys.exit(
                    "Cannot perform registration, image {} "
                    "not found".format(img_path)
                )
            if not img_path.endswith(".nii"):
                if img_path.endswith((".tiff", ".tif")):
                    nii_path = "{}{}".format(
                        os.path.splitext(img_path)[0], ".nii"
                    )
                    brainio.tiff_to_nii(img_path, nii_path)
                    setattr(self, img_path_var_name, nii_path)
                else:
                    raise RegistrationError(
                        "Cannot perform registration, image {} "
                        "not in supported format".format(img_path)
                    )

    def _prepare_openmp_thread_flag(self):
        self.openmp_flag = "-omp {}".format(self.n_processes)

    def _prepare_affine_reg_cmd(self):
        cmd = "{} {} -flo {} -ref {} -aff {} -res {}".format(
            self.reg_params.affine_reg_program_path,
            self.reg_params.format_affine_params().strip(),
            self.brain_of_atlas_img_path,
            self.dataset_img_path,
            self.paths.affine_matrix_path,
            self.paths.tmp__affine_registered_atlas_brain_path,
        )

        if self.n_processes is not None:
            cmd += " " + self.openmp_flag
        return cmd

    def register_affine(self):
        """
        Performs affine registration of the average brain of the atlas to the
        sample using nifty_reg reg_aladin

        :return:
        :raises RegistrationError: If any error was detected during
            registration.
        """
        try:
            safe_execute_command(
                self._prepare_affine_reg_cmd(),
                self.paths.tmp__affine_log_file_path,
                self.paths.tmp__affine_error_path,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Affine registration failed; {}".format(err)
            )

    def _prepare_freeform_reg_cmd(self):
        cmd = "{} {} -aff {} -flo {} -ref {} -cpp {} -res {}".format(
            self.reg_params.freeform_reg_program_path,
            self.reg_params.format_freeform_params().strip(),
            self.paths.affine_matrix_path,
            self.brain_of_atlas_img_path,
            self.dataset_img_path,
            self.paths.control_point_file_path,
            self.paths.tmp__freeform_registered_atlas_brain_path,
        )

        if self.n_processes is not None:
            cmd += " " + self.openmp_flag
        return cmd

    def register_freeform(self):
        """
        Performs freeform (elastic) registration of the average brain of the
        atlas to the sample brain using nifty_reg reg_f3d

        :return:
        :raises RegistrationError: If any error was detected during
            registration.
        """
        try:
            safe_execute_command(
                self._prepare_freeform_reg_cmd(),
                self.paths.tmp__freeform_log_file_path,
                self.paths.tmp__freeform_error_file_path,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Freeform registration failed; {}".format(err)
            )

    def generate_inverse_transforms(self):
        self.generate_inverse_affine()
        self.register_inverse_freeform()

    def _prepare_invert_affine_cmd(self):
        cmd = "{} -invAff {} {}".format(
            self.reg_params.transform_program_path,
            self.paths.affine_matrix_path,
            self.paths.invert_affine_matrix_path,
        )
        return cmd

    def generate_inverse_affine(self):
        """
        Inverts the affine transform to allow for quick registration of the
        sample onto the atlas
        :return:
        :raises RegistrationError: If any error was detected during
            registration.

        """
        logging.debug("Generating inverse affine transform")
        try:
            safe_execute_command(
                self._prepare_invert_affine_cmd(),
                self.paths.tmp__invert_affine_log_file,
                self.paths.tmp__invert_affine_error_file,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Generation of inverted affine transform failed; "
                "{}".format(err)
            )

    def _prepare_inverse_freeform_reg_cmd(self):
        cmd = "{} {} -aff {} -flo {} -ref {} -cpp {} -res {}".format(
            self.reg_params.freeform_reg_program_path,
            self.reg_params.format_freeform_params().strip(),
            self.paths.invert_affine_matrix_path,
            self.dataset_img_path,
            self.brain_of_atlas_img_path,
            self.paths.inverse_control_point_file_path,
            self.paths.tmp__inverse_freeform_registered_atlas_brain_path,
        )

        if self.n_processes is not None:
            cmd += " " + self.openmp_flag
        return cmd

    def register_inverse_freeform(self):
        """
        Performs freeform (elastic) registration of the sample to the
        atlas using nifty_reg reg_f3d

        :return:
        :raises RegistrationError: If any error was detected during
            registration.
        """
        logging.debug("Registering sample to atlas")

        try:
            safe_execute_command(
                self._prepare_inverse_freeform_reg_cmd(),
                self.paths.tmp__inverse_freeform_log_file_path,
                self.paths.tmp__inverse_freeform_error_file_path,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Inverse freeform registration failed; {}".format(err)
            )

    def _prepare_segmentation_cmd(self, floating_image_path, dest_img_path):
        cmd = "{} {} -cpp {} -flo {} -ref {} -res {}".format(
            self.reg_params.segmentation_program_path,
            self.reg_params.format_segmentation_params().strip(),
            self.paths.control_point_file_path,
            floating_image_path,
            self.dataset_img_path,
            dest_img_path,
        )
        return cmd

    def segment(self):
        """
        Registers the atlas to the sample (propagates the transformation
        computed for the average brain of the atlas to the atlas itself).


        :return:
        :raises SegmentationError: If any error was detected during the
            propagation.
        """
        try:
            safe_execute_command(
                self._prepare_segmentation_cmd(
                    self.atlas_img_path, self.paths.registered_atlas_img_path
                ),
                self.paths.tmp__segmentation_log_file,
                self.paths.tmp__segmentation_error_file,
            )
        except SafeExecuteCommandError as err:
            SegmentationError("Segmentation failed; {}".format(err))

    def register_hemispheres(self):
        """
        Registers the hemispheres atlas to the sample (propagates the
        transformation computed for the average brain of the atlas to the
        hemispheres atlas itself).

        :return:
        :raises RegistrationError: If any error was detected during the
            propagation.
        """
        try:
            safe_execute_command(
                self._prepare_segmentation_cmd(
                    self.hemispheres_img_path,
                    self.paths.registered_hemispheres_img_path,
                ),
                self.paths.tmp__segmentation_log_file,
                self.paths.tmp__segmentation_error_file,
            )
        except SafeExecuteCommandError as err:
            SegmentationError("Segmentation failed; {}".format(err))
