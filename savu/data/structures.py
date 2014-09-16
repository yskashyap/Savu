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

"""
.. module:: structures
   :platform: Unix
   :synopsis: Classes which describe the main data types for passing between
              plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import h5py


class RawData(object):
    """
    Descriptor for raw data
    """

    def __init__(self):
        super(RawData, self).__init__()
        self.data = None
        self.image_key = None
        self.rotation_angle = None
        self.control = None

    def populate_from_nexus(self, path):
        """Load a plugin.

        :param path: The full path of the NeXus file to load
        :type path: str.

        """
        f = h5py.File(path, 'r')
        self.data = f['entry1/tomo_entry/instrument/detector/data']
        self.image_key = f['entry1/tomo_entry/instrument/detector/image_key']
        self.rotation_angle = f['entry1/tomo_entry/sample/rotation_angle']
        self.control = f['entry1/tomo_entry/control/data']


class ProjectionData(object):
    """
    Descriptor for corrected projection data
    """

    def __init__(self):
        super(RawData, self).__init__()
        self.data = None
        self.rotation_angle = None


class VolumeData(object):
    """
    Descriptor for volume data
    """

    def __init__(self):
        super(RawData, self).__init__()
        self.data = None
