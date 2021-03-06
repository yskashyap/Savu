# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from savu.data.process_data import CitationInfomration
from savu.data.structures import ProjectionData

"""
.. module:: vo_centering
   :platform: Unix
   :synopsis: A plugin to find the center of rotation per frame

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.plugins.pass_through_plugin import PassThroughPlugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.data import structures

import scipy.ndimage as ndi

import numpy as np
import scipy.fftpack as fft

from savu.plugins.utils import register_plugin


@register_plugin
class VoCentering(PassThroughPlugin, CpuPlugin):
    """
    A plugin to calculate the center of rotation using the Vo Method
    """

    def __init__(self):
        super(VoCentering, self).__init__("VoCentering")

    def _create_mask(self, sino, pixel_step=0.5):
        fsino = np.vstack([sino, sino])
        mask = np.zeros(fsino.shape, dtype=np.bool)
        count = float(mask.shape[1]/2)
        for i in np.arange(mask.shape[0]/2, -1, -1):
            if count < 0:
                mask[i, :] = True
                mask[-i, :] = True
            else:
                mask[i, int(count):-(int(count+1))] = True
                mask[-i, int(count):-(int(count+1))] = True
            count -= pixel_step
        return mask

    def _scan(self, cor_positions, in_sino):
        mask = self._create_mask(in_sino)
        values = []
        sino = np.nan_to_num(in_sino)
        for i in cor_positions:
            ssino = ndi.interpolation.shift(sino, (0, i), mode='wrap')
            fsino = np.vstack([ssino, ssino[:, ::-1]])
            fftsino = fft.fftshift(fft.fft2(fsino))
            values.append(np.sum(np.abs(fftsino)*mask))
        vv = np.array(values)
        vv = abs(vv)
        return cor_positions[vv.argmin()]

    def get_filter_frame_type(self):
        """
        This filter processes sinograms

         :returns:  structures.CD_SINOGRAM
        """
        return structures.CD_SINOGRAM

    def get_max_frames(self):
        """
        This filter processes 1 frame at a time

         :returns:  1
        """
        return 1

    def required_data_type(self):
        """
        The input for this plugin is ProjectionData as it needs to be corrected

        :returns:  ProjectionData
        """
        return ProjectionData

    def process_frame(self, data):
        data = data.squeeze()
        width = data.shape[1]/4
        step = width/10.
        point = 0.0

        while step > 0.01:
            x = np.arange(point-width, point+width, step)
            point = self._scan(x, data)
            width = step
            step = width/10.

        cor = (data.shape[1]/2.0) - point
        return {'center_of_rotation': cor}

    def get_citation_inforamtion(self):
        cite_info = CitationInfomration()
        cite_info.description = \
            ("The center of rotation for this reconstruction was calculated " +
             "automatically using the method described in this work")
        cite_info.bibtex = \
            ("@article{vo2014reliable,\n" +
             "title={Reliable method for calculating the center of rotation " +
             "in parallel-beam tomography},\n" +
             "author={Vo, Nghia T and Drakopoulos, Michael and Atwood, " +
             "Robert C and Reinhard, Christina},\n" +
             "journal={Optics Express},\n" +
             "volume={22},\n" +
             "number={16},\n" +
             "pages={19078--19086},\n" +
             "year={2014},\n" +
             "publisher={Optical Society of America}\n" +
             "}")
        cite_info.endnote = \
            ("%0 Journal Article\n" +
             "%T Reliable method for calculating the center of rotation in " +
             "parallel-beam tomography\n" +
             "%A Vo, Nghia T\n" +
             "%A Drakopoulos, Michael\n" +
             "%A Atwood, Robert C\n" +
             "%A Reinhard, Christina\n" +
             "%J Optics Express\n" +
             "%V 22\n" +
             "%N 16\n" +
             "%P 19078-19086\n" +
             "%@ 1094-4087\n" +
             "%D 2014\n" +
             "%I Optical Society of America")
        cite_info.doi = "http://dx.doi.org/10.1364/OE.22.019078"
        return cite_info
