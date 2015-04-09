#################################################################################
#
#  importSPE.py - imports SPE version 3.0 files
#
#  usage: out = importSPE(file)
#	      file: SPE file to import
#         out: list of arrays (each list item is an individual ROI)
#              each array indices are:
#                      (height,width,frame)
#
#  Requires struct, xml.etree.ElementTree, numpy
#
#   Copyright (c) 2015 Jon A. Dieringer
#
#################################################################################

import struct
import xml.etree.ElementTree as ET
import numpy as np

def importSPE(file):

    f = open(file,"rb")

    # Readout SPE_version. If not >=3.0 then abort.
    f.seek(1992)
    SPE_version = struct.unpack('f',f.read(4))[0]
    if SPE_version < 3:
   	return 'SPE version 3.0 or greater is required';
	
    # Find the location of the xml containing the data formatting and read it out	
    f.seek(678)
    xml_offset = struct.unpack('Q',f.read(8))[0]
    f.seek(xml_offset)
    xml = f.read()
    tree = ET.fromstring(xml);
	
    # This DataBlock contains the frame information and its children the ROI information
    datablockroot = tree.findall('{http://www.princetoninstruments.com/spe/2009}DataFormat')[0].getchildren()[0]
    n_roi = len(datablockroot.getchildren())
    n_frames = int(datablockroot.get('count'))
    frame_size = int(datablockroot.get('size'))
    frame_stride = int(datablockroot.get('stride'))

    # Determine the data format
    if datablockroot.get('pixelFormat')=='MonochromeFloating32':
   	dataformat = 'f'
    elif datablockroot.get('pixelFormat')=='MonochromeUnsigned32':
	dataformat = 'I'
    elif datablockroot.get('pixelFormat')=='MonochromeUnsigned16':
	dataformat = 'H'
    else:
	dataformat = ''

    # Collect information about the ROIs		
    roi_size = np.zeros(n_roi,dtype='int32')
    roi_stride = np.zeros(n_roi,dtype='int32')
    roi_height = np.zeros(n_roi,dtype='int32')
    roi_width = np.zeros(n_roi,dtype='int32')

    for i in range(n_roi):
	roi_size[i] = int(datablockroot.getchildren()[i].get('size'))
	roi_stride[i] = int(datablockroot.getchildren()[i].get('stride'))
	roi_height[i] = int(datablockroot.getchildren()[i].get('height'))
	roi_width[i] = int(datablockroot.getchildren()[i].get('width'))

    roi_stride_offset = np.insert(roi_stride,0,0)
    roi_stride_sum = np.cumsum(roi_stride_offset)

    # Read out the data ROI by ROI and append to the list 'data'	
    data = []
    for r in range(n_roi):
	buffer = np.zeros((roi_height[r],roi_width[r],n_frames))
	for fr in range(n_frames):
	   f.seek(4100+fr*frame_stride+roi_stride_sum[r])
	   buffer[:,:,fr] = np.reshape(struct.unpack(str(roi_size[r]/2)+dataformat,f.read(roi_size[r])),(roi_height[r],roi_width[r]))
	data.append(buffer)
	buffer = None

    # Close the SPE file		
    f.close()
	
    # Return the data list
    return data;


##################################################################################	
#	
#	The MIT License (MIT)
#
#	Copyright (c) 2015 Jon A. Dieringer
#
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the "Software"), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in all
#	copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#	SOFTWARE.
#
##################################################################################
