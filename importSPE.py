import struct
import xml.etree.ElementTree as ET
import numpy as np

f = open(file,"rb")
f.seek(1992)
SPE_version = struct.unpack('f',f.read(4))[0]
f.seek(678)
xml_offset = struct.unpack('Q',f.read(8))[0]
f.seek(xml_offset)
xml = f.read()
tree = ET.fromstring(xml);
datablockroot = tree.findall('{http://www.princetoninstruments.com/spe/2009}DataFormat')[0].getchildren()[0]
n_roi = len(datablockroot.getchildren())
n_frames = int(datablockroot.get('count'))
frame_size = int(datablockroot.get('size'))
frame_stride = int(datablockroot.get('stride'))
if datablockroot.get('pixelFormat')=='MonochromeFloating32':
    dataformat = 'f'
elif datablockroot.get('pixelFormat')=='MonochromeUnsigned32':
    dataformat = 'I'
elif datablockroot.get('pixelFormat')=='MonochromeUnsigned16':
    dataformat = 'H'
else:
    dataformat = ''
    
roi_size = zeros(n_roi,dtype='int32')
roi_stride = zeros(n_roi,dtype='int32')
roi_height = zeros(n_roi,dtype='int32')
roi_width = zeros(n_roi,dtype='int32')

for i in range(n_roi):
    roi_size[i] = int(datablockroot.getchildren()[i].get('size'))
    roi_stride[i] = int(datablockroot.getchildren()[i].get('stride'))
    roi_height[i] = int(datablockroot.getchildren()[i].get('height'))
    roi_width[i] = int(datablockroot.getchildren()[i].get('width'))

roi_stride_offset = np.insert(roi_stride,0,0)
roi_stride_sum = np.cumsum(roi_stride_offset)

data = []
for r in range(n_roi):
    buffer = zeros((roi_height[r],roi_width[r],n_frames))
    for fr in range(n_frames):
        f.seek(4100+fr*frame_stride+roi_stride_sum[r])
        buffer[:,:,fr] = np.reshape(struct.unpack(str(roi_size[r]/2)+dataformat,f.read(roi_size[r])),(roi_height[r],roi_width[r]))
    data.append(buffer)
    buffer = None
f.close()
