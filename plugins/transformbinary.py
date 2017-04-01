'''<b>Smooth</b> smooths (i.e., blurs) images
<h>
This module allows you to smooth (blur) images, which can be helpful to remove artifacts of a particular size.
Note that smoothing can be a time-consuming process.
'''

import numpy as np
import scipy.ndimage as scind
from centrosome.filter import median_filter, bilateral_filter, circular_average_filter
from centrosome.smooth import circular_gaussian_kernel
from centrosome.smooth import fit_polynomial
from centrosome.smooth import smooth_with_function_and_mask

import cellprofiler.cpimage as cpi
import cellprofiler.cpmodule as cpm
import cellprofiler.settings as cps
from cellprofiler.gui.help import HELP_ON_MEASURING_DISTANCES, HELP_ON_PIXEL_INTENSITIES
from cellprofiler.settings import YES, NO

import imctools.library as imclib

from matplotlib.widgets import Slider, Button, RadioButtons

REOVE_OUTLIER = 'Remove single hot pixels'
DISTANCE_BORDER = 'Distance to border'

class TransformBinary(cpm.CPModule):
    module_name = 'Transform Binary'
    category = "Image Processing"
    variable_revision_number = 1

    def create_settings(self):
        self.image_name = cps.ImageNameSubscriber('Select the input image',
                                                  cps.NONE)

        self.transformed_image_name = cps.ImageNameProvider(
            "Name the transformed image",
            'DistanceImage')

        self.transform_method = cps.Choice(
                'Select a transformation',
                [DISTANCE_BORDER], doc="""
            <ul>
            <li><i>%(DISTANCE_BORDER)s</i> Transforms the binary image to an
            eucledian distance transform to the border between the binary
            regions.</li>
            </ul>""" % globals())


    def settings(self):
        return [self.image_name, self.transformed_image_name]

    def visible_settings(self):
        result = [self.image_name, self.transformed_image_name,
                  self.transform_method]
        return result

    def run_per_layer(self, image, channel):
        if channel >= 0:
            pixel_data = image.pixel_data[:,:,channel].squeeze()
        else:
            pixel_data = image.pixel_data
        if self.transform_method.value == DISTANCE_BORDER:
            output_pixels = imclib.distance_to_border(pixel_data)
        else:
            raise ValueError("Unsupported smoothing method: %s" %
self.transform_method.value)
        return output_pixels

    def run(self, workspace):
        image = workspace.image_set.get_image(self.image_name.value,
                                              must_be_grayscale=False)

        output_pixels =image.pixel_data.copy()

        if len(image.pixel_data.shape) ==3:
            for i in range(image.pixel_data.shape[2]):
                output_pixels[:,:,i] = self.run_per_layer(image, i)
        else:
            output_pixels = self.run_per_layer(image, -1)

        output_image = cpi.Image(output_pixels, parent_image=image)
        workspace.image_set.add(self.transformed_image_name.value,
                                output_image)
        workspace.display_data.pixel_data = image.pixel_data
        workspace.display_data.output_pixels = output_pixels

    def display(self, workspace, figure):
        figure.set_subplots((2, 1))
        ax1 = figure.subplot_imshow_grayscale(0, 0,
                                        workspace.display_data.pixel_data,
                                        "Original: %s" %
                                        self.image_name.value)
        ax2 = figure.subplot_imshow_grayscale(1, 0,
                                        workspace.display_data.output_pixels,
                                        "Filtered: %s" %
                                        self.transformed_image_name.value,
                                        sharexy=figure.subplot(0, 0))
        # import pdb; pdb.set_trace()
        #schan1 = Slider(ax1, 'channel 1', 0, nchannel1,  valinit=1)
        #schan2 = Slider(ax2, 'channel 2', 0, nchannel2, valinit=1)

        # def update(val):
        #     channel1 = schan1.val
        #     channel2 = schan2.val
        #
        # schan1.on_changed(update)
        # schan2.on_changed(update)

    def upgrade_settings(self, setting_values, variable_revision_number,
                         module_name, from_matlab):

        return setting_values, variable_revision_number, from_matlab
