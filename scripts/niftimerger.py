import numpy
import vtk
import nifti
import sys
import bar

def rgb(hexVal):
    """
    Converts html hexidecimal color value into RGB color components tuple.
    
    @type  hexVal: C{str}
    @param hexVal: html hexicedimal color string.
    
    @rtype: C{(int,int,int)}
    @return: RGB color components tuple.
    """
    n = eval('0x' + hexVal[1:])
    return (n>>16)&0xff, (n>>8)&0xff, n&0xff

template = 'volume_%s.nii.gz'
path = sys.argv[1]
barpath  = sys.argv[2]
outarr = None

threshold = 20

idx = bar.barIndexer.fromXML(barpath)

for group in sys.argv[3:]:
    i = nifti.NiftiImage(path + template % group)
    print group
    if outarr == None:
        print "first"
        ds=i.data.shape
        outarr = numpy.zeros((ds[0],ds[1],ds[2]), dtype=numpy.uint8)
        carr = numpy.zeros((ds[0],ds[1],ds[2],3), dtype=numpy.uint8)
    
    print "another"
    temp = i.data
    temp[temp < threshold] = False
    temp[temp >= threshold] = True
    
    volCurNewXor = numpy.logical_xor(temp, outarr)
    volXorAndNew = numpy.logical_and(temp,volCurNewXor)
    print idx.groups[group].id
    print long(idx.groups[group].id)
    print long(idx.groups[group].id)-200000
    outarr[volXorAndNew] = long(idx.groups[group].id)-200000
    carr[volXorAndNew] = numpy.array(rgb(idx.groups[group].fill))

d = vtk.vtkImageData()
d.SetNumberOfScalarComponents(3)
d.SetDimensions(*ds)
o=i.header['qoffset']
p=i.header['pixdim'][1:4]
d.SetOrigin(o[2],o[1],o[0])
d.SetSpacing(p[2],p[1],p[0])
d.SetScalarTypeToUnsignedChar()
d.AllocateScalars()

print d.GetPointData().GetScalars()
for i in range(ds[2]):
    print i
    for j in range(ds[1]):
        for k in range(ds[0]):
            id = d.ComputePointId((k,j,i))
            d.GetPointData().GetScalars().SetTuple3(id, *map(float,carr[k,j,i]))

x = vtk.vtkImagePermute()
x.SetFilteredAxes(2,1,0)
x.SetInput(d)

cast = vtk.vtkImageCast()
cast.SetInput(x.GetOutput())
cast.SetOutputScalarTypeToFloat()
cast.Update()

cast2 = vtk.vtkImageCast()
cast2.SetInput(cast.GetOutput())
cast2.SetOutputScalarTypeToUnsignedInt()
cast2.Update()

w = vtk.vtkStructuredPointsWriter()
w.SetInput(cast2.GetOutput())
w.SetFileName('xxxxxc-pw.vtk')
w.Update()
